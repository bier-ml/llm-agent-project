from typing import Any, Dict, List

"""
This module provides mock implementations of financial analysis functions.
These functions are used for testing and demonstration purposes.
"""


def get_stock_price(symbol: str) -> float:
    """
    Get current price for a stock or cryptocurrency.

    Args:
        symbol: The ticker symbol of the stock/crypto (e.g., 'AAPL', 'BTC')

    Returns:
        float: Current price of the specified symbol
    """
    # Mock implementation - returns fixed value for testing
    return 100.0


def analyze_news(symbol: str, days: int = 7) -> List[Dict[str, str]]:
    """
    Get recent news analysis for a symbol.

    Args:
        symbol: The ticker symbol to analyze
        days: Number of days of news to analyze (default: 7)

    Returns:
        List[Dict]: List of news items with date, headline, and sentiment
    """
    # Mock implementation - returns sample news data
    return [{"date": "2024-03-20", "headline": "Sample news", "sentiment": "positive"}]


def get_market_analysis(symbol: str) -> Dict[str, str]:
    """
    Get detailed market analysis for a symbol.

    Args:
        symbol: The ticker symbol to analyze

    Returns:
        Dict: Market analysis including trend, support, and resistance levels
    """
    # Mock implementation - returns sample analysis data
    return {"trend": "bullish", "support": "95.0", "resistance": "105.0"}


def get_investment_recommendation(portfolio: Dict[str, Any]) -> Dict[str, str]:
    """
    Get investment recommendations for a portfolio.

    Args:
        portfolio: Dictionary containing portfolio details and holdings

    Returns:
        Dict: Investment recommendation and reasoning
    """
    # Mock implementation - returns sample recommendation
    return {"recommendation": "buy", "reason": "Strong growth potential"}


# List of all available mock functions for use in the agent system
MOCK_FUNCTIONS = [
    get_stock_price,
    analyze_news,
    get_market_analysis,
    get_investment_recommendation,
]
