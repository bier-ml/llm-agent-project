import pytest
from unittest.mock import Mock, patch
from src.client.services import ToolCallHandler


@pytest.fixture
def tool_handler():
    return ToolCallHandler()


@pytest.fixture
def mock_coin_price_df():
    import pandas as pd

    return pd.DataFrame({"price": [29000.0, 29500.0, 30000.0]}, index=pd.date_range("2021-01-01", periods=3))


@pytest.mark.asyncio
async def test_handle_unknown_tool_type(tool_handler):
    result = await tool_handler.handle({"type": "unknown_tool"})
    assert "error" in result
    assert "Unknown tool type" in result["error"]


@pytest.mark.asyncio
@patch("src.client.service.coin_price_service.CoinPriceService.get_coin_price_history")
async def test_handle_coin_price(mock_get_price, tool_handler, mock_coin_price_df):
    mock_get_price.return_value = mock_coin_price_df

    result = await tool_handler.handle({"type": "get_coin_price", "coin_id": "bitcoin", "currency": "usd"})

    assert result["coin_id"] == "bitcoin"
    assert result["price"] == 30000.0
    assert result["currency"] == "usd"


@pytest.mark.asyncio
@patch("src.client.service.coin_price_service.CoinPriceService.get_coin_price_history")
async def test_handle_coin_history(mock_get_history, tool_handler, mock_coin_price_df):
    mock_get_history.return_value = mock_coin_price_df

    result = await tool_handler.handle({"type": "get_coin_history", "coin_id": "bitcoin", "days": 30})

    assert result["coin_id"] == "bitcoin"
    assert result["current_price"] == 30000.0
    assert result["highest_price"] == 30000.0
    assert result["lowest_price"] == 29000.0


@pytest.mark.asyncio
@patch("src.client.service.financial_news_service.FinancialNewsService.get_financial_news")
async def test_handle_news(mock_get_news, tool_handler):
    mock_get_news.return_value = [
        {"title": "Test News", "description": "Test Description", "content": "Test Content", "url": "http://test.com"}
    ]

    result = await tool_handler.handle({"type": "get_news"})
    assert "articles" in result
    assert "Test News" in result["articles"]


@pytest.mark.asyncio
async def test_handle_user_response(tool_handler):
    test_message = "Test message"
    result = await tool_handler.handle({"type": "response_to_user", "message": test_message})

    assert result is not None
    assert isinstance(result, dict)
    assert result["type"] == "user_response"
    assert result["message"] == test_message


@pytest.mark.asyncio
async def test_handle_user_response_no_message(tool_handler):
    result = await tool_handler.handle({"type": "response_to_user"})

    assert result is not None
    assert isinstance(result, dict)
    assert "error" in result
    assert "No message provided" in result["error"]
