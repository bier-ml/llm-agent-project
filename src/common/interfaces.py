from typing import Any, Dict, Optional, Protocol

from pydantic import BaseModel


class Message(BaseModel):
    """Represents a message to be processed"""

    content: str
    user_id: str
    llm_type: Optional[str] = None
    metadata: Dict[str, Any] = {}


class MessageProcessor(Protocol):
    """Protocol defining the interface for message processors"""

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Process a message and return a response"""
        ...


class ServiceConnector(Protocol):
    """Protocol defining the interface for service connections"""

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to a service endpoint"""
        ...
