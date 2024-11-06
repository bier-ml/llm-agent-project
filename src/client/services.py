from typing import Any, Dict

import httpx

from src.client.service.coin_price_service import CoinPriceService
from src.client.service.financial_news_service import FinancialNewsService
from src.common.interfaces import ServiceConnector


class AgentServiceConnector(ServiceConnector):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def send_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to agent service."""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/{endpoint}", json=data)
            return response.json()


class ToolCallHandler:
    def __init__(self):
        self.coin_price_service = CoinPriceService()
        self.news_service = FinancialNewsService()

    async def handle(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from the agent."""
        tool_type = tool_call.get("type")

        handlers = {
            "get_coin_price": self._handle_coin_price,
            "get_coin_history": self._handle_coin_history,
            "get_news": self._handle_news,
            "get_market_news": self._handle_market_news,
            "get_coin_news": self._handle_coin_news,
        }

        handler = handlers.get(tool_type)
        if handler:
            return await handler(tool_call)

        return {"error": f"Unknown tool type: {tool_type}"}

    async def _handle_coin_price(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get current coin price."""
        coin_id = tool_call.get("coin_id")
        vs_currency = tool_call.get("currency", "usd")

        if not coin_id:
            return {"error": "No coin_id provided"}

        try:
            df = self.coin_price_service.get_coin_price_history(
                coin_id=coin_id, vs_currency=vs_currency, days=1
            )
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
            df = self.coin_price_service.get_coin_price_history(
                coin_id=coin_id, vs_currency=vs_currency, days=days
            )

            return {
                "coin_id": coin_id,
                "currency": vs_currency,
                "days": days,
                "current_price": df.iloc[-1]["price"] if not df.empty else None,
                "highest_price": df["price"].max() if not df.empty else None,
                "lowest_price": df["price"].min() if not df.empty else None,
                "price_change": (df.iloc[-1]["price"] - df.iloc[0]["price"])
                if not df.empty
                else None,
                "start_date": df.index[0].isoformat() if not df.empty else None,
                "end_date": df.index[-1].isoformat() if not df.empty else None,
            }
        except Exception as e:
            return {"error": f"Failed to fetch coin history: {str(e)}"}

    async def _handle_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get general financial news."""
        try:
            articles = self.news_service.get_financial_news(
                keywords="stock OR crypto", page_size=5
            )

            return {
                "articles": [
                    {
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["url"],
                        "published_at": article["publishedAt"],
                    }
                    for article in articles
                ]
            }
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
            return {"error": f"Failed to fetch market news: {str(e)}"}

    async def _handle_coin_news(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Get cryptocurrency specific news."""
        coin_id = tool_call.get("coin_id", "")

        try:
            keywords = f"cryptocurrency OR crypto OR {coin_id}"
            articles = self.news_service.get_financial_news(
                keywords=keywords, page_size=5
            )

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
