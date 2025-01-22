"""
Core interfaces and models used across the application.
Defines the contract for message processing and service communication.
"""

from typing import Any, Dict, Optional, Protocol

from pydantic import BaseModel


class Message(BaseModel):
    """
    Represents a message to be processed by the system.

    Attributes:
        content: The actual message content
        user_id: Unique identifier for the message sender
        llm_type: Optional type of LLM to use for processing
        metadata: Additional contextual information
    """

    content: str
    user_id: str
    llm_type: Optional[str] = None
    metadata: Dict[str, Any] = {}


class MessageProcessor(Protocol):
    """Protocol defining the interface for message processors."""

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """
        Process a message and return a response.

        Args:
            message: The Message object to process

        Returns:
            Dict containing the processed response
        """
        ...


class ServiceConnector(Protocol):
    """Protocol defining the interface for service connections."""

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to a service endpoint.

        Args:
            endpoint: The service endpoint to call
            data: The request payload

        Returns:
            Dict containing the service response
        """
        ...
