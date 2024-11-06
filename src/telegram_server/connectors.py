from typing import Any, Dict

import httpx

from src.common.interfaces import ServiceConnector


class ClientServiceConnector(ServiceConnector):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to client service."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/{endpoint}", json=data)
            return response.json()
