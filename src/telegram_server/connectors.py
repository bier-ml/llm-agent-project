import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


class ClientServiceConnector:
    """A connector class for making HTTP requests to the client service API.

    This class handles all HTTP communication with the client service,
    implementing proper timeout handling and error logging.

    Attributes:
        base_url (str): The base URL of the client service API
        timeout_settings (httpx.Timeout): Custom timeout configuration for API requests
    """

    def __init__(self, base_url: str):
        """Initialize the connector with base URL and timeout settings.

        Args:
            base_url (str): The base URL for the client service API
        """
        self.base_url = base_url
        # Add large timeout settings for LLM processing
        self.timeout_settings = httpx.Timeout(
            timeout=3000.0,  # 50 minutes total timeout
            connect=1000.0,  # ~16 minutes for connection establishment
            read=2000.0,  # ~33 minutes for reading response
            write=1000.0,  # ~16 minutes for sending request
        )

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an HTTP POST request to the specified client API endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to
            data (Dict[str, Any]): The request payload to send

        Returns:
            Dict[str, Any]: The JSON response from the API

        Raises:
            httpx.TimeoutException: If the request times out
            Exception: For any other errors during the request
        """
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
