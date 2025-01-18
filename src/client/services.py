import logging
from typing import Any, Dict, Optional, Tuple

import httpx

from src.client.service.coin_price_service import CoinPriceService
from src.client.service.financial_news_service import FinancialNewsService
from src.common.interfaces import ServiceConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentServiceConnector(ServiceConnector):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        # Add timeout configurations
        self.timeout_settings = httpx.Timeout(
            timeout=3000.0,  # 30 seconds for the entire operation
            connect=1000.0,  # 10 seconds for connecting
            read=2000.0,  # 20 seconds for reading
            write=1000.0,  # 10 seconds for writing
        )

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to agent service."""
        self.logger.info(f"Sending request to {endpoint} with data: {data}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout_settings) as client:
                self.logger.debug(f"Making POST request to {self.base_url}/{endpoint}")
                response = await client.post(f"{self.base_url}/{endpoint}", json=data)

                # Check if the response was successful
                response.raise_for_status()

                response_data = response.json()
                self.logger.info(f"Received response from agent: {response_data}")
                return response_data

        except httpx.TimeoutException as e:
            error_msg = f"Timeout while connecting to agent service: {str(e)}"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg) from e

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"Request error occurred: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        except Exception as e:
            error_msg = f"Error sending request to agent: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e


class ToolCallHandler:
    def __init__(self):
        self.coin_price_service = CoinPriceService()
        self.news_service = FinancialNewsService()
        self.logger = logging.getLogger(__name__)

    async def handle(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from the agent."""
        tool_type = tool_call.get("type")
        self.logger.info(f"Handling tool call of type: {tool_type}")
        self.logger.debug(f"Tool call data: {tool_call}")

        handlers = {
            "get_coin_price": self._handle_coin_price,
            "get_coin_history": self._handle_coin_history,
            "get_news": self._handle_news,
            "get_market_news": self._handle_market_news,
            "get_coin_news": self._handle_coin_news,
            "response_to_user": self._handle_user_response,
        }

        handler = handlers.get(tool_type)
        if handler:
            try:
                result = await handler(tool_call)
                self.logger.info(f"Successfully handled {tool_type} tool call")
                self.logger.debug(f"Tool call result: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error handling {tool_type} tool call: {str(e)}")
                return

        self.logger.warning(f"Unknown tool type received: {tool_type}")
        return {"error": f"Unknown tool type: {tool_type}"}

    async def _handle_coin_price(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get current coin price."""
        coin_id = tool_call.get("coin_id")
        vs_currency = tool_call.get("currency", "usd")

        if not coin_id:
            return {"error": "No coin_id provided"}

        try:
            df = self.coin_price_service.get_coin_price_history(coin_id=coin_id, vs_currency=vs_currency, days=1)
            current_price = df.iloc[-1]["price"] if not df.empty else None

            return {
                "coin_id": coin_id,
                "price": current_price,
                "currency": vs_currency,
                "timestamp": df.index[-1].isoformat() if not df.empty else None,
            }
        except Exception as e:
            return {"error": f"Failed to fetch coin price: {str(e)}"}

    async def _handle_coin_history(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get coin price history."""
        coin_id = tool_call.get("coin_id")
        vs_currency = tool_call.get("currency", "usd")
        days = tool_call.get("days", 30)

        if not coin_id:
            return {"error": "No coin_id provided"}

        try:
            df = self.coin_price_service.get_coin_price_history(coin_id=coin_id, vs_currency=vs_currency, days=days)

            return {
                "coin_id": coin_id,
                "currency": vs_currency,
                "days": days,
                "current_price": df.iloc[-1]["price"] if not df.empty else None,
                "highest_price": df["price"].max() if not df.empty else None,
                "lowest_price": df["price"].min() if not df.empty else None,
                "price_change": (df.iloc[-1]["price"] - df.iloc[0]["price"]) if not df.empty else None,
                "start_date": df.index[0].isoformat() if not df.empty else None,
                "end_date": df.index[-1].isoformat() if not df.empty else None,
            }
        except Exception as e:
            return {"error": f"Failed to fetch coin history: {str(e)}"}

    async def _handle_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get general financial news."""
        try:
            articles = self.news_service.get_financial_news(keywords="stock OR crypto", page_size=5)

            return {"articles": self.news_service.print_news(articles=articles)}
        except Exception as e:
            return {"error": f"Failed to fetch news: {str(e)}"}

    async def _handle_market_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get stock market specific news."""
        try:
            articles = self.news_service.get_financial_news(
                keywords="stock market OR trading OR investment", page_size=5
            )

            return {
                "category": "stock_market",
                "articles": self.news_service.print_news(articles=articles),
            }
        except Exception as e:
            return {"error": f"Failed to fetch market news: {str(e)}"}

    async def _handle_coin_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get cryptocurrency specific news."""
        coin_id = tool_call.get("coin_id", "")

        try:
            keywords = f"cryptocurrency OR crypto OR {coin_id}"
            articles = self.news_service.get_financial_news(keywords=keywords, page_size=5)

            return {
                "coin_id": coin_id,
                "articles": [
                    {
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["url"],
                        "published_at": article["publishedAt"],
                    }
                    for article in articles
                ],
            }
        except Exception as e:
            return {"error": f"Failed to fetch crypto news: {str(e)}"}

    async def _handle_user_response(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Handle direct responses to the user."""
        logger.info("got tool call: " + tool_call)
        message = tool_call.get("message")
        if not message:
            return {"error": "No message provided for user response"}

        return {"type": "user_response", "message": message}


class TelegramServiceConnector(ServiceConnector):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.timeout_settings = httpx.Timeout(
            timeout=3000.0,  # 30 seconds for the entire operation
            connect=1000.0,  # 10 seconds for connecting
            read=2000.0,  # 20 seconds for reading
            write=1000.0,  # 10 seconds for writing
        )

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the Telegram service."""
        self.logger.info(f"Sending request to {endpoint} with data: {data}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout_settings) as client:
                response = await client.post(f"{self.base_url}/{endpoint}", json=data)

                # Check if the response was successful
                response.raise_for_status()

                response_data = response.json()
                self.logger.info(f"Received response from Telegram service: {response_data}")
                return response_data

        except httpx.TimeoutException as e:
            error_msg = f"Timeout while connecting to Telegram service: {str(e)}"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg) from e

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"Request error occurred: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

        except Exception as e:
            error_msg = f"Error sending request to Telegram service: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
