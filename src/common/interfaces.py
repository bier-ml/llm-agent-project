from typing import Any, Dict, Protocol

from pydantic import BaseModel


class Message(BaseModel):
    """Represents a message to be processed"""

    content: str
    metadata: Dict[str, Any] = {}


class MessageProcessor(Protocol):
    """Protocol defining the interface for message processors"""

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Process a message and return a response"""
        ...
