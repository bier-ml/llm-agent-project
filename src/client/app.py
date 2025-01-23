import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from rank_bm25 import BM25Okapi
from tortoise import Tortoise

from src.client.services import (
    AgentServiceConnector,
    TelegramServiceConnector,
    ToolCallHandler,
)
from src.common.interfaces import Message
from src.common.models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    yield
    # Shutdown
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)

# Tortoise ORM config
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.getenv("POSTGRES_HOST", "postgres"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "user": os.getenv("POSTGRES_USER", "ivan"),
                "password": os.getenv("POSTGRES_PASSWORD", "ivan"),
                "database": os.getenv("POSTGRES_DB", "ivan_db"),
            },
        }
    },
    "apps": {
        "models": {
            "models": ["src.common.models"],
            "default_connection": "default",
        }
    },
}


class ClientService:
    """Main service class handling client-side operations including message processing and news monitoring.

    Manages connections to agent and telegram services, handles tool calls, and processes user messages
    and portfolio updates. Also implements periodic news checking with different strategies.
    """

    def __init__(self):
        self.agent_connector = AgentServiceConnector(base_url=os.getenv("AGENT_SERVICE_URL", "http://agent:8001"))
        self.telegram_connector = TelegramServiceConnector(
            base_url=os.getenv("TELEGRAM_SERVICE_URL", "http://telegram_bot:8002")
        )
        self.tool_handler = ToolCallHandler()
        self.logger = logging.getLogger(__name__)
        self.last_news_state = None
        self.news_strategy = os.getenv("NEWS_STRATEGY", "original")

        # Initialize Tortoise-ORM
        asyncio.create_task(self.init_db())

    async def init_db(self):
        """Initialize database connection with Tortoise-ORM."""
        try:
            await Tortoise.init(config=TORTOISE_ORM)
            self.logger.info("Successfully initialized Tortoise-ORM")
        except Exception as e:
            self.logger.error(f"Failed to initialize database connection: {str(e)}")
            raise

    def _format_results_message(self, results: list, original_message: str) -> str:
        """Format results into a human-readable message for the agent."""
        results_text = "\n".join(f"- For action '{result.get('type', 'unknown')}': {result}" for result in results)

        return (
            f"I've gathered the information you requested. Here are the results:\n\n"
            f"{results_text}\n\n"
            f"Given this information, please provide a response to the user's original message: "
            f"'{original_message}'"
        )

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Process incoming user messages and route them to appropriate handlers.

        Args:
            message: Message object containing user input and metadata

        Returns:
            Dict containing response message or error details

        Raises:
            HTTPException: If processing fails or times out
        """
        self.logger.info(f"Processing message: {message}")
        try:
            # Fetch user data for context
            user, _ = await User.get_or_create(telegram_id=message.user_id)

            # Check if message is portfolio-related
            if "update portfolio" in message.content.lower():
                return await self.update_portfolio(message)
            if "portfolio" in message.content.lower():
                return await self.check_portfolio(message)

            current_context = {
                "content": message.content,
                "user_id": message.user_id,
                "llm_type": message.llm_type,
                "metadata": message.metadata,
                "portfolio": user.portfolio,  # Add portfolio to context
            }

            return await self.call_llm_agent(current_context)

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise

    async def check_portfolio(self, message: Message) -> Dict[str, Any]:
        """Retrieve user's portfolio preferences from database.

        Args:
            message: Message object containing user ID

        Returns:
            Dict containing portfolio details or error message
        """
        self.logger.info(f"Checking portfolio for message: {message}")

        try:
            # Fetch user preferences using Tortoise-ORM
            user, created = await User.get_or_create(telegram_id=message.user_id)

            if created:
                self.logger.info(f"Created new user entry for user_id: {message.user_id}")

            # Format the response with user preferences
            response = f"Here are your portfolio preferences: {user.portfolio}\n"

            return {"message": response}

        except Exception as e:
            self.logger.error(f"Error checking portfolio preferences: {str(e)}")
            return {
                "message": "Sorry, I encountered an error while checking your portfolio preferences. "
                "Please try again later."
            }

    async def update_portfolio(self, message: Message) -> Dict[str, Any]:
        """Handle portfolio update requests."""
        self.logger.info(f"Updating portfolio for message: {message}")

        try:
            # Update user preferences using Tortoise-ORM
            user, created = await User.get_or_create(telegram_id=message.user_id)

            if created:
                self.logger.info(f"Created new user entry for user_id: {message.user_id}")

            user.portfolio = [item.strip() for item in message.content.split("[")[1].split("]")[0].split(",")]
            await user.save()

            self.logger.info(f"Updated portfolio for user_id: {message.user_id}")

            return {"message": "Successfully updated your portfolio preferences."}

        except Exception as e:
            self.logger.error(f"Error updating portfolio preferences: {str(e)}")
            return {
                "message": "Sorry, I encountered an error while updating your portfolio preferences. "
                "Please try again later."
            }

    async def call_llm_agent(self, current_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the LLM agent interaction flow."""
        while True:
            # Enhance the prompt with portfolio context if available
            if current_context.get("portfolio"):
                portfolio_context = (
                    f"\nContext: The user's current portfolio contains: {', '.join(current_context['portfolio'])}. "
                    "Please consider their existing investments when providing recommendations."
                )
                if isinstance(current_context["content"], str):
                    current_context["content"] += portfolio_context

            # Get next action from agent
            response = await self.agent_connector.send_request("process", current_context)
            self.logger.info(f"Received response from agent: {response}")

            if not isinstance(response, dict):
                return {"error": "Invalid response format from agent"}

            thought = response.get("thought", "")
            actions = response.get("actions", [])

            # If no actions or response_to_user, return the thought to user
            if not actions or (len(actions) == 1 and actions[0]["name"] == "response_to_user"):
                if actions and actions[0]["name"] == "response_to_user":
                    return {"message": actions[0].get("argument", "")}
                return {"message": thought}

            # Execute the actions and collect results
            results = []
            for action in actions:
                tool_call = {
                    "type": action["name"],
                    **(
                        action.get("argument", {})
                        if isinstance(action.get("argument"), dict)
                        else {"coin_symbol": action.get("argument", "")}
                    ),
                }
                result = await self.tool_handler.handle(tool_call)
                results.append(result)

            # Create human-readable message with results
            results_message = self._format_results_message(
                results=results,
                original_message=current_context["content"],
            )

            # Update context with results for next iteration
            current_context = {
                "content": results_message,
                "user_id": current_context["user_id"],
                "llm_type": current_context["llm_type"],
                "metadata": current_context["metadata"],
            }

    async def check_news(self):
        await asyncio.sleep(6000)  # Disabled for live features demo
        """Periodically check the news and notify users based on configured strategy."""
        while True:
            try:
                current_news = await self.tool_handler.handle({"type": "get_news"})
                self.logger.info(f"Fetched current news: {current_news}")

                if self.last_news_state != current_news:
                    if self.news_strategy == "bm25":
                        await self._process_news_bm25(current_news)
                    else:
                        await self._process_news_original(current_news)

                    self.last_news_state = current_news

            except Exception as e:
                self.logger.error(f"Error checking news: {str(e)}")

            await asyncio.sleep(600)  # Wait for 10 minutes before checking again

    async def _process_news_original(self, current_news: dict):
        """Original implementation of news processing."""
        users = await User.all()
        for user in users:
            portfolio_context = (
                f"Given that the user's portfolio contains: {', '.join(user.portfolio)}, "
                f"please analyze what's different from the last news state: "
                f"'{self.last_news_state}' in comparison to the current news: '{current_news}'. "
                f"You should analyze the impact that the last state had on the market and how it changed "
                f"with the last news in place, specifically considering their current investments. "
                f"What might they invest into, what should they hold and what should they avoid? "
                f"Please only provide \"response_to_user\" action with \"message\" with results of your analysis:"
            )

            self.logger.info(f"Sending personalized news analysis prompt to agent for user {user.telegram_id}")
            result = await self.agent_connector.send_request(
                "process",
                {
                    "content": portfolio_context,
                    "user_id": str(user.telegram_id),
                    "llm_type": "xmlBasedLLM",
                    "portfolio": user.portfolio,
                },
            )

            try:
                result = next(
                    action["argument"]
                    for action in result.get("actions", [])
                    if action.get("name") == "response_to_user"
                )
            except StopIteration:
                raise ValueError("No 'response_to_user' action found in the response")

            await self.telegram_connector.send_request(
                "send_message",
                {
                    "chat_id": user.telegram_id,
                    "message": result,
                },
            )

    def _calculate_relevance_scores(self, news_content: str, users: List[User]) -> List[Tuple[User, float]]:
        """Calculate BM25 relevance scores between news and user portfolios."""
        # Tokenize news content
        news_tokens = news_content.lower().split()

        # Create corpus from user portfolios
        corpus = [" ".join(user.portfolio).lower() for user in users]

        # Initialize BM25
        bm25 = BM25Okapi([doc.split() for doc in corpus])

        # Calculate relevance scores
        scores = bm25.get_scores(news_tokens)

        # Pair users with their scores
        user_scores = list(zip(users, scores))

        # Sort by score in descending order
        return sorted(user_scores, key=lambda x: x[1], reverse=True)

    async def _process_news_bm25(self, current_news: dict):
        """Process news using BM25 algorithm to match relevant news to user portfolios.

        Calculates relevance scores between news content and user portfolios using BM25,
        then sends personalized analysis only to users with high relevance scores.

        Args:
            current_news: Dictionary containing latest news articles
        """
        # Get all users
        users = await User.all()

        # Extract text content from news for matching
        news_content = self._extract_news_content(current_news)

        # Calculate relevance scores
        relevant_users = self._calculate_relevance_scores(news_content, users)

        # Process only users with relevance score above threshold
        threshold = 0.1  # Adjust this threshold based on your needs
        for user, score in relevant_users:
            if score < threshold:
                continue

            # Generate personalized analysis for relevant users
            analysis_prompt = (
                f"Based on the user's portfolio: {', '.join(user.portfolio)}, "
                f"and their relevance score of {score:.2f} to the following news: '{current_news}', "
                f"please provide a targeted analysis of how this news affects their specific investments. "
                f"Focus on direct impacts to their portfolio assets and potential opportunities or risks. "
                f"Please only provide \"response_to_user\" action with \"message\" containing your analysis."
            )

            self.logger.info(
                f"Sending BM25-filtered news analysis for user {user.telegram_id} " f"with relevance score {score:.2f}"
            )

            result = await self.agent_connector.send_request(
                "process",
                {
                    "content": analysis_prompt,
                    "user_id": str(user.telegram_id),
                    "llm_type": "xmlBasedLLM",
                    "portfolio": user.portfolio,
                },
            )

            try:
                message = next(
                    action["argument"]
                    for action in result.get("actions", [])
                    if action.get("name") == "response_to_user"
                )
            except StopIteration:
                raise ValueError("No 'response_to_user' action found in the response")

            await self.telegram_connector.send_request(
                "send_message",
                {
                    "chat_id": user.telegram_id,
                    "message": message,
                },
            )

    def _extract_news_content(self, news: dict) -> str:
        """Extract text content from news dictionary for relevance matching.

        Handles both single articles and lists of articles, combining title,
        description and content fields into a single text string.

        Args:
            news: News dictionary or list of news articles

        Returns:
            Extracted text content as string
        """
        if not news:
            return ""

        # Handle list of articles
        if isinstance(news, list):
            # Combine all articles into one text
            article_texts = []
            for article in news:
                article_content = []
                # Extract relevant fields from each article
                if isinstance(article, dict):
                    if article.get("title"):
                        article_content.append(article["title"])
                    if article.get("description"):
                        article_content.append(article["description"])
                    if article.get("content"):
                        article_content.append(article["content"])
                article_texts.append(" ".join(article_content))
            return " ".join(article_texts)

        # Handle single article or unexpected format
        if isinstance(news, dict):
            content_parts = []
            if news.get("title"):
                content_parts.append(news["title"])
            if news.get("description"):
                content_parts.append(news["description"])
            if news.get("content"):
                content_parts.append(news["content"])
            return " ".join(content_parts)

        # Fallback for unexpected formats
        return str(news)


# Start the periodic news check
client_service = ClientService()
asyncio.create_task(client_service.check_news())


@app.post("/process_message")
async def process_message(message: Message):
    logger.info(f"Received message processing request: {message}")
    try:
        message.llm_type = "xmlBasedLLM"

        response = await client_service.process_message(message)
        logger.info(f"Successfully processed message: {response}")

        if isinstance(response, dict):
            if "error" in response:
                raise HTTPException(status_code=500, detail=response["error"])
            return response

        return {"error": "Invalid response format"}

    except TimeoutError as e:
        error_msg = "The LLM service is taking too long to respond. Please try again later."
        logger.error(f"{error_msg} Original error: {str(e)}")
        raise HTTPException(status_code=504, detail=error_msg)

    except Exception as e:
        error_msg = "An error occurred while processing your message"
        logger.error(f"{error_msg}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/tool_call")
async def handle_tool_call(tool_call: Dict[str, Any]):
    logger.info(f"Received tool call request: {tool_call}")
    try:
        result = await client_service.tool_handler.handle(tool_call)
        logger.info(f"Successfully handled tool call: {result}")
        return result
    except Exception as e:
        logger.error(f"Error handling tool call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
