from typing import Any, Dict, List


def get_stock_price(symbol: str) -> float:
    """Get current price for a stock or cryptocurrency"""
    # Mock implementation
    return 100.0


def analyze_news(symbol: str, days: int = 7) -> List[Dict[str, str]]:
    """Get recent news analysis for a symbol"""
    # Mock implementation
    return [{"date": "2024-03-20", "headline": "Sample news", "sentiment": "positive"}]


def get_market_analysis(symbol: str) -> Dict[str, str]:
    """Get detailed market analysis for a symbol"""
    # Mock implementation
    return {"trend": "bullish", "support": "95.0", "resistance": "105.0"}


def get_investment_recommendation(portfolio: Dict[str, Any]) -> Dict[str, str]:
    """Get investment recommendations for a portfolio"""
    # Mock implementation
    return {"recommendation": "buy", "reason": "Strong growth potential"}


MOCK_FUNCTIONS = [
    get_stock_price,
    analyze_news,
    get_market_analysis,
    get_investment_recommendation,
]
