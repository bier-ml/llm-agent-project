import pandas as pd
import requests


class CoinPriceService:
    def __init__(self, base_url="https://api.coingecko.com/api/v3"):
        self.base_url = base_url

    def get_coin_price_history(
        self, coin_id: str, vs_currency: str = "usd", days: int = 30
    ) -> pd.DataFrame:
        """
        Fetch historical price data for a given id from CoinGecko.

        Args:
            coin_id (str): Cryptocurrency id (e.g., 'bitcoin').
            vs_currency (str): Currency to compare against (e.g., 'usd').
            days (int): Number of days for historical data.

        Returns:
            pd.DataFrame: DataFrame containing price data.
        """
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days, "interval": "daily"}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {response.status_code}")

        data = response.json()

        if "prices" in data:
            prices = data["prices"]
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        else:
            print(f"No price data available for {coin_id}.")
            return pd.DataFrame(columns=["timestamp", "price"])


if __name__ == "__main__":
    coin_service = CoinPriceService()

    df = coin_service.get_coin_price_history("hamster", days=90)
    print(df)
