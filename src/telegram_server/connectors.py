import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ClientServiceConnector:
    def __init__(self, base_url: str):
        self.base_url = base_url
        # Add large timeout settings for LLM processing
        self.timeout_settings = httpx.Timeout(
            timeout=3000.0,  # 3000 seconds total
            connect=1000.0,  # 1000 seconds for connecting
            read=2000.0,  # 2000 seconds for reading
            write=1000.0,  # 1000 seconds for writing
        )

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to client API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout_settings) as client:
                logger.info(f"Sending request to {endpoint} with data: {data}")
                response = await client.post(f"{self.base_url}/{endpoint}", json=data)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error while connecting to client API: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error sending request to client API: {str(e)}")
            raise
