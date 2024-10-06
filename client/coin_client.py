import requests
import pandas as pd


def get_coin_price_history(symbol: str, vs_currency: str = 'usd', days: int = 30) -> pd.DataFrame:
    """
    Fetch historical price data for a given symbol from CoinGecko.

    Args:
        symbol (str): Cryptocurrency symbol (e.g., 'bitcoin').
        vs_currency (str): Currency to compare against (e.g., 'usd').
        days (int): Number of days for historical data.

    Returns:
        pd.DataFrame: DataFrame containing price data.
    """
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart'
    params = {'vs_currency': vs_currency, 'days': days, 'interval': 'daily'}
    response = requests.get(url, params=params)
    data = response.json()

    # Convert to DataFrame
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df


if __name__ == '__main__':
    df = get_coin_price_history('hamster', days=90)
    print(df)
