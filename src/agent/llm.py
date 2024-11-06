import os
from typing import Any, Dict, Optional

import openai

from src.common.interfaces import Message, MessageProcessor


class LLMProcessor(MessageProcessor):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        openai.api_key = self.api_key
        self.model = "gpt-4"  # Can be configured via environment variable if needed
        self.system_prompt = """You are IVAN (Interactive Venture Analysis Network), 
        a financial advisor specializing in stocks and cryptocurrencies. 
        Your responses should be clear, professional, and focused on providing 
        actionable financial insights. Always consider:
        1. Current market trends
        2. Risk management
        3. Portfolio diversification
        4. User's context and history
        """

    async def _create_chat_completion(
        self, messages: list[Dict[str, str]], temperature: float = 0.7
    ) -> str:
        """Create a chat completion using OpenAI's API."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model, messages=messages, temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            # Log the error here if you have logging set up
            raise Exception(f"Error in LLM processing: {str(e)}")

    def _format_message_history(
        self, message: Message, chat_history: Optional[list] = None
    ) -> list[Dict[str, str]]:
        """Format the message and chat history for the LLM."""
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history)

        # Add the current message
        messages.append({"role": "user", "content": message.content})

        return messages

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Process a message and return a response."""
        try:
            # Format messages for the LLM
            messages = self._format_message_history(message)

            # Get response from LLM
            response_content = await self._create_chat_completion(messages)

            # Parse any potential actions from the response
            # This could be enhanced to detect specific actions like:
            # - Fetching stock prices
            # - Analyzing news
            # - Updating portfolio
            actions = self._parse_actions(response_content)

            return {"message": response_content, "actions": actions}
        except Exception as e:
            return {
                "message": f"I apologize, but I encountered an error: {str(e)}",
                "actions": None,
            }

    def _parse_actions(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse any actions from the LLM response."""
        # This is a simple implementation that could be enhanced
        # to detect and parse specific actions from the response
        actions = None

        # Example action detection (you can expand this based on your needs)
        if "get_stock_price" in response.lower():
            actions = {"type": "get_stock_price"}
        elif "analyze_news" in response.lower():
            actions = {"type": "analyze_news"}
        elif "update_portfolio" in response.lower():
            actions = {"type": "update_portfolio"}

        return actions

    async def get_market_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get market analysis for a specific symbol."""
        prompt = f"Provide a detailed market analysis for {symbol}, including current trends and potential risks."
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        response = await self._create_chat_completion(messages, temperature=0.5)
        return {"analysis": response}

    async def get_investment_recommendation(
        self, portfolio: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get investment recommendations based on current portfolio."""
        portfolio_str = "\n".join([f"- {k}: {v}" for k, v in portfolio.items()])
        prompt = f"""Based on the following portfolio, provide investment recommendations:
        {portfolio_str}
        Consider market conditions, risk tolerance, and diversification."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        response = await self._create_chat_completion(messages, temperature=0.7)
        return {"recommendation": response}
