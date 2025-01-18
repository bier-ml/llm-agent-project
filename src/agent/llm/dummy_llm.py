from textwrap import dedent
from typing import Any, Dict, List, Optional

from src.agent.llm.base_llm import BaseLLMProcessor
from src.common.interfaces import Message


class DummyStockProcessor(BaseLLMProcessor):
    def __init__(self):
        self.system_prompt = "I am a stock-loving AI assistant."

    async def _create_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        # Always return the same response suggesting to buy stocks
        return dedent("""
            Thought: The user would definitely benefit from investing in the stock market right now. 
            The market conditions are perfect for buying opportunities.

            Action: response_to_user("You should consider investing in stocks! The market is full of opportunities right now. 
            Have you looked into tech stocks? They're particularly interesting at the moment.")
            End Action
        """)

    def _format_message_history(self, message: Message, chat_history: Optional[list] = None) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.append({"role": "user", "content": message.content})
        return messages

    def _parse_action_block(self, content: str) -> Dict[str, Any]:
        # Always return the response_to_user function call
        return {
            "function_name": "response_to_user",
            "function_params": {
                "message": "You should consider investing in stocks! The market is full of opportunities right now. Have you looked into tech stocks? They're particularly interesting at the moment."
            },
        }

    async def process_message(self, message: Message) -> Dict[str, Any]:
        messages = self._format_message_history(message)
        response_content = await self._create_chat_completion(messages)

        return {
            "message": response_content,
            "thought": self._extract_thought(response_content),
            "function": self._parse_action_block(response_content),
        }

    def _extract_thought(self, content: str) -> Optional[str]:
        return "The user would definitely benefit from investing in the stock market right now. The market conditions are perfect for buying opportunities."
