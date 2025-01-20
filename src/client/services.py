import logging
from typing import Any, Dict

import httpx

from src.client.service.coin_price_service import CoinPriceService
from src.client.service.financial_news_service import FinancialNewsService
from src.common.interfaces import ServiceConnector
from src.client.service.stock_price_service import StockPriceService

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
        self.stock_price_service = StockPriceService()
        self.logger = logging.getLogger(__name__)

    async def handle(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from the agent."""
        tool_type = tool_call.get("type")
        self.logger.info(f"Handling tool call of type: {tool_type}")
        self.logger.debug(f"Tool call data: {tool_call}")

        handlers = {
            "get_coin_price": self._handle_coin_price,
            "get_coin_history": self._handle_coin_history,
            "get_stock_price": self._handle_stock_price,
            "get_stock_history": self._handle_stock_history,
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
                result["type"] = tool_type  # Include the tool type in the response
                return result
            except Exception as e:
                self.logger.error(f"Error handling {tool_type} tool call: {str(e)}")
                return {"type": tool_type, "error": f"Error handling {tool_type} tool call: {str(e)}"}

        self.logger.warning(f"Unknown tool type received: {tool_type}")
        return {"type": tool_type, "error": f"Unknown tool type: {tool_type}"}

    async def _handle_coin_price(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get current coin price."""
        coin_symbol = tool_call.get("coin_symbol")
        vs_currency = tool_call.get("currency", "usd")

        if not coin_symbol:
            return {"error": "No coin_symbol provided"}

        try:
            df = self.coin_price_service.get_coin_price_history(coin_symbol=coin_symbol, vs_currency=vs_currency, days=1)
            current_price = df.iloc[-1]["price"] if not df.empty else None

            return {
                "type": "get_coin_price",
                "coin_symbol": coin_symbol,
                "price": current_price,
                "currency": vs_currency,
                "timestamp": df.index[-1].isoformat() if not df.empty else None,
            }
        except Exception as e:
            return {"type": "get_coin_price", "error": f"Failed to fetch coin price: {str(e)}"}

    async def _handle_coin_history(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get coin price history."""
        coin_symbol = tool_call.get("coin_symbol")
        vs_currency = tool_call.get("currency", "usd")
        days = tool_call.get("days", 30)

        if not coin_symbol:
            return {"error": "No coin_symbol provided"}

        try:
            df = self.coin_price_service.get_coin_price_history(coin_symbol=coin_symbol, vs_currency=vs_currency, days=days)

            return {
                "type": "get_coin_history",
                "coin_symbol": coin_symbol,
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
            return {"type": "get_coin_history", "error": f"Failed to fetch coin history: {str(e)}"}

    async def _handle_stock_price(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get current stock price."""
        stock_symbol = tool_call.get("coin_symbol")

        if not stock_symbol:
            return {"error": "No stock_symbol provided"}

        try:
            df = self.stock_price_service.get_stock_price_history(symbol=stock_symbol, interval="daily", outputsize="compact")
            current_price = df.iloc[-1]["Close"] if not df.empty else None

            return {
                "type": "get_stock_price",
                "stock_symbol": stock_symbol,
                "price": current_price,
                "timestamp": df.index[-1].isoformat() if not df.empty else None,
            }
        except Exception as e:
            return {"type": "get_stock_price", "error": f"Failed to fetch stock price: {str(e)}"}

    async def _handle_stock_history(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get stock price history."""
        stock_symbol = tool_call.get("stock_symbol")
        interval = tool_call.get("interval", "daily")
        outputsize = tool_call.get("outputsize", "compact")

        if not stock_symbol:
            return {"error": "No stock_symbol provided"}

        try:
            df = self.stock_price_service.get_stock_price_history(symbol=stock_symbol, interval=interval, outputsize=outputsize)

            return {
                "type": "get_stock_history",
                "stock_symbol": stock_symbol,
                "interval": interval,
                "outputsize": outputsize,
                "current_price": df.iloc[-1]["Close"] if not df.empty else None,
                "highest_price": df["High"].max() if not df.empty else None,
                "lowest_price": df["Low"].min() if not df.empty else None,
                "price_change": (df.iloc[-1]["Close"] - df.iloc[0]["Close"]) if not df.empty else None,
                "start_date": df.index[0].isoformat() if not df.empty else None,
                "end_date": df.index[-1].isoformat() if not df.empty else None,
            }
        except Exception as e:
            return {"type": "get_stock_history", "error": f"Failed to fetch stock history: {str(e)}"}

    async def _handle_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get general financial news."""
        try:
            articles = self.news_service.get_financial_news(keywords="stock OR crypto", page_size=5)

            return {"type": "get_news", "articles": self.news_service.print_news(articles=articles)}
        except Exception as e:
            return {"type": "get_news", "error": f"Failed to fetch news: {str(e)}"}

    async def _handle_market_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get stock market specific news."""
        try:
            articles = self.news_service.get_financial_news(
                keywords="stock market OR trading OR investment", page_size=5
            )

            return {
                "type": "get_market_news",
                "category": "stock_market",
                "articles": self.news_service.print_news(articles=articles),
            }
        except Exception as e:
            return {"type": "get_market_news", "error": f"Failed to fetch market news: {str(e)}"}

    async def _handle_coin_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get cryptocurrency specific news."""
        coin_symbol = tool_call.get("coin_symbol", "")

        try:
            keywords = f"cryptocurrency OR crypto OR {coin_symbol}"
            articles = self.news_service.get_financial_news(keywords=keywords, page_size=5)

            return {
                "type": "get_coin_news",
                "coin_symbol": coin_symbol,
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
            return {"type": "get_coin_news", "error": f"Failed to fetch crypto news: {str(e)}"}

    async def _handle_user_response(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Handle direct responses to the user."""
        self.logger.info(f"got tool call: {tool_call}")
        message = tool_call.get("message")
        if not message:
            return {"error": "No message provided for user response"}

        return {"type": "response_to_user", "message": message}


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
