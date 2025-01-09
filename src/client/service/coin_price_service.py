import logging

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class CoinPriceService:
    def __init__(self, base_url="https://api.coingecko.com/api/v3"):
        self.base_url = base_url
        logger.info("CoinPriceService initialized")

    def get_coin_price_history(self, coin_id: str, vs_currency: str = "usd", days: int = 30) -> pd.DataFrame:
        logger.info(f"Fetching price history for {coin_id} in {vs_currency} for {days} days")
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days, "interval": "daily"}

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                logger.error(f"Error fetching data: {response.status_code}")
                raise Exception(f"Error fetching data: {response.status_code}")

            data = response.json()

            if "prices" in data:
                prices = data["prices"]
                df = pd.DataFrame(prices, columns=["timestamp", "price"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df.set_index("timestamp", inplace=True)
                logger.info(f"Successfully fetched price history for {coin_id}")
                return df
            else:
                logger.warning(f"No price data available for {coin_id}")
                return pd.DataFrame(columns=["timestamp", "price"])
        except Exception as e:
            logger.error(f"Error fetching price history for {coin_id}: {str(e)}")
            raise


if __name__ == "__main__":
    coin_service = CoinPriceService()

    df = coin_service.get_coin_price_history("hamster", days=90)
    print(df)
