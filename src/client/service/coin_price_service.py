import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class CoinPriceService:
    """
    A service class for fetching cryptocurrency price data from CoinAPI.

    This service provides methods to retrieve historical price data for various cryptocurrencies
    using the CoinAPI REST API.
    """

    def __init__(self, base_url="https://rest.coinapi.io/v1", api_key=None):
        """
        Initialize the CoinPriceService.

        Args:
            base_url (str): The base URL for the CoinAPI REST API. Defaults to 'https://rest.coinapi.io/v1'.
            api_key (str, optional): The API key for CoinAPI. If not provided, will attempt to load from environment variable.

        Raises:
            ValueError: If no API key is provided or found in environment variables.
        """
        self.base_url = base_url
        self.api_key = api_key or os.getenv("COINAPI_KEY")
        if not self.api_key:
            raise ValueError("API key is required")
        logger.info("CoinPriceService initialized")

    def get_coin_price_history(self, coin_symbol: str, vs_currency: str = "USD", days: int = 30) -> pd.DataFrame:
        """
        Fetch historical price data for a specified cryptocurrency.

        Args:
            coin_symbol (str): The symbol of the cryptocurrency (e.g., 'BTC' for Bitcoin).
            vs_currency (str): The currency to compare against (e.g., 'USD'). Defaults to 'USD'.
            days (int): Number of days of historical data to fetch. Defaults to 30.

        Returns:
            pd.DataFrame: A DataFrame containing the historical price data with datetime index.
                        Columns include 'price' (closing price for each day).

        Raises:
            Exception: If there's an error fetching the data from the API.
        """
        logger.info(f"Fetching price history for {coin_symbol} in {vs_currency} for {days} days")

        time_end = pd.Timestamp.now()
        time_start = time_end - pd.Timedelta(days=days)

        url = f"{self.base_url}/exchangerate/{coin_symbol}/{vs_currency}/history"
        headers = {"X-CoinAPI-Key": self.api_key}
        params = {
            "period_id": "1DAY",
            "time_start": time_start.isoformat(timespec="seconds") + "Z",
            "time_end": time_end.isoformat(timespec="seconds") + "Z",
            "limit": 100,
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                logger.error(f"Error fetching data: {response.status_code}")
                raise Exception(f"Error fetching data: {response.status_code}")

            data = response.json()
            logger.info(f"Successfully fetched historical exchange rates for {coin_symbol}")

            # Create a DataFrame with the fetched rates
            df = pd.DataFrame(data, columns=["time_period_start", "rate_close"])
            df["time_period_start"] = pd.to_datetime(df["time_period_start"])
            df.set_index("time_period_start", inplace=True)
            df.rename(columns={"rate_close": "price"}, inplace=True)

            return df
        except Exception as e:
            logger.error(f"Error fetching price history for {coin_symbol}: {str(e)}")
            raise


if __name__ == "__main__":
    coin_service = CoinPriceService()

    df = coin_service.get_coin_price_history("BTC", days=30)
    print(df)
