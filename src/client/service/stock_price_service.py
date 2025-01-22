import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class StockPriceService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ALPHA_VANTAGE_KEY")
        if not api_key:
            logger.error("ALPHA_VANTAGE_KEY environment variable is not set")
            raise ValueError("ALPHA_VANTAGE_KEY environment variable is not set")
        self.api_key = api_key
        logger.info("StockPriceService initialized successfully")

    def get_stock_price_history(self, symbol: str, interval: str = "daily", outputsize: str = "compact"):
        logger.info(f"Fetching stock price history for {symbol} with interval: {interval}")
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_" + interval.upper(),
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": outputsize,
            "datatype": "json",
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if "Time Series (Daily)" in data or "Time Series (Intraday)" in data:
                time_series_key = "Time Series (Daily)" if "Time Series (Daily)" in data else "Time Series (Intraday)"
                prices = data[time_series_key]
                df = pd.DataFrame.from_dict(prices, orient="index")
                df.columns = ["Open", "High", "Low", "Close", "Volume"]
                df.index = pd.to_datetime(df.index)
                df = df.astype(float)
                logger.info(f"Successfully fetched stock price data for {symbol}")
                return df
            else:
                logger.error(f"Error fetching stock price data: {data.get('Note', 'Unknown error')}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"An error occurred while fetching stock price data: {e}")
            return pd.DataFrame()


# Usage Example
if __name__ == "__main__":
    load_dotenv()

    stock_service = StockPriceService()

    stock_symbol = "NVDA"
    stock_prices = stock_service.get_stock_price_history(stock_symbol)

    print(stock_prices)
