import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.client.service.coin_price_service import CoinPriceService


@pytest.fixture
def coin_service():
    return CoinPriceService()


@pytest.fixture
def mock_response():
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        "prices": [
            [1609459200000, 29000.0],  # 2021-01-01
            [1609545600000, 29500.0],  # 2021-01-02
            [1609632000000, 30000.0],  # 2021-01-03
        ]
    }
    return mock


def test_init():
    service = CoinPriceService(base_url="https://custom.api.com")
    assert service.base_url == "https://custom.api.com"


@patch("requests.get")
def test_get_coin_price_history_success(mock_get, coin_service, mock_response):
    mock_get.return_value = mock_response

    df = coin_service.get_coin_price_history("bitcoin", "usd", 3)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "price" in df.columns
    assert df.index.name == "timestamp"
    assert df.iloc[0]["price"] == 29000.0


@patch("requests.get")
def test_get_coin_price_history_error_response(mock_get, coin_service):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        coin_service.get_coin_price_history("invalid_coin")

    assert "Error fetching data: 404" in str(exc_info.value)


@patch("requests.get")
def test_get_coin_price_history_no_data(mock_get, coin_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    df = coin_service.get_coin_price_history("bitcoin")

    assert isinstance(df, pd.DataFrame)
    assert df.empty
    assert list(df.columns) == ["timestamp", "price"]
