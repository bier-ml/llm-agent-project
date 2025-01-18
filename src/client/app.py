from datetime import datetime
from typing import Dict, Any
import asyncio
import logging
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from src.client.services import (
    AgentServiceConnector,
    ToolCallHandler,
    TelegramServiceConnector,
)
from src.common.interfaces import Message
from src.telegram_server.telegram_bot import IvanTelegramBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class ClientService:
    def __init__(self):
        self.agent_connector = AgentServiceConnector(base_url=os.getenv("AGENT_SERVICE_URL", "http://agent:8001"))
        self.telegram_connector = TelegramServiceConnector(
            base_url=os.getenv("TELEGRAM_SERVICE_URL", "http://telegram_bot:8002")
        )
        self.tool_handler = ToolCallHandler()
        self.logger = logging.getLogger(__name__)
        self.last_news_state = None

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
        self.logger.info(f"Processing message: {message}")
        try:
            current_context = {
                "content": message.content,
                "user_id": message.user_id,
                "llm_type": message.llm_type,
                "metadata": message.metadata,
            }

            while True:
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
                            else {"coin_id": action.get("argument", "")}
                        ),
                    }
                    result = await self.tool_handler.handle(tool_call)
                    results.append(result)

                # Create human-readable message with results
                results_message = self._format_results_message(
                    results=results,
                    original_message=message.content,
                )

                # Update context with results for next iteration
                current_context = {
                    "content": results_message,
                    "user_id": message.user_id,
                    "llm_type": message.llm_type,
                    "metadata": message.metadata,
                }

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise

    async def check_news(self):
        """Periodically check the news and notify the user if anything changed."""
        while True:
            try:
                # Fetch current news
                current_news = await self.tool_handler.handle({"type": "get_news"})
                self.logger.info(f"Fetched current news: {current_news}")

                # Compare with the last news state
                if self.last_news_state != current_news:
                    prompt = (
                        f"Please analyze what's different from the last news state: "
                        f"'{self.last_news_state}' in comparison to the current news: '{current_news}'. You should analyze the impact that the last state had on the market and how it changed with the last news in place, what might I invest into, what should I hold and what should I avoid? Please only provide \"response_to_user\" action with \"message\" with results of your analysis:"
                    )
                    self.logger.info(f"Sending news change prompt to agent: {prompt}")
                    result = await self.agent_connector.send_request(
                        "process",
                        {
                            "content": prompt,
                            "user_id": "user1",
                            "llm_type": "jsonBasedLLM",
                        },
                    )

                    logger.warn(result)

                    # Extract the 'argument' from the 'actions' list
                    try:
                        result = next(
                            action["argument"]
                            for action in result.get("actions", [])
                            if action.get("name") == "response_to_user"
                        )
                    except StopIteration:
                        raise ValueError("No 'response_to_user' action found in the response")

                    # Send the result via Telegram
                    await self.telegram_connector.send_request(
                        "send_message",
                        {
                            "chat_id": 123,  # TODO: your chat id here; env variable?
                            "message": result,
                        },
                    )
                # Update the last news state
                self.last_news_state = current_news

            except Exception as e:
                self.logger.error(f"Error checking news: {str(e)}")

            # Wait for 30 minutes before checking again
            await asyncio.sleep(60)


# Start the periodic news check
client_service = ClientService()
asyncio.create_task(client_service.check_news())


@app.post("/process_message")
async def process_message(message: Message):
    logger.info(f"Received message processing request: {message}")
    try:
        message.llm_type = "jsonBasedLLM"

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
