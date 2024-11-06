from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.common.interfaces import Message


class CodeAction:
    def __init__(self, code: str, function_calls: List[Dict[str, Any]]):
        self.code = code
        self.function_calls = function_calls


class BaseLLMProcessor(ABC):
    """Abstract base class for LLM processors."""

    @abstractmethod
    async def process_message(self, message: Message) -> Dict[str, Any]:
        """
        Process a message and return a response with structured function calls.

        Args:
            message (Message): The input message to process

        Returns:
            Dict[str, Any]: A dictionary containing:
                - message: The raw response content
                - thought: Extracted thought process (if any)
                - function: Parsed function call details
        """
        pass

    @abstractmethod
    def _format_message_history(
        self, message: Message, chat_history: Optional[list] = None
    ) -> List[Dict[str, str]]:
        """
        Format the message and chat history for the LLM.

        Args:
            message (Message): The current message to format
            chat_history (Optional[list]): Previous chat history

        Returns:
            List[Dict[str, str]]: Formatted messages for the LLM
        """
        pass

    @abstractmethod
    async def _create_chat_completion(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> str:
        """
        Create a chat completion using the LLM's API.

        Args:
            messages (List[Dict[str, str]]): The formatted messages
            temperature (float): Sampling temperature for generation

        Returns:
            str: The LLM's response content
        """
        pass

    @abstractmethod
    def _parse_action_block(self, content: str) -> Dict[str, Any]:
        """
        Parse the action block to extract function name and parameters.

        Args:
            content (str): The response content to parse

        Returns:
            Dict[str, Any]: Parsed function call details
        """
        pass

    @abstractmethod
    def _extract_thought(self, content: str) -> Optional[str]:
        """
        Extract the thought process from the response content.

        Args:
            content (str): The response content to parse

        Returns:
            Optional[str]: The extracted thought process, if found
        """
        pass
