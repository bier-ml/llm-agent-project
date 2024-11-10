from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


class BenchmarkDataLoader:
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the benchmark data loader.

        Args:
            data_path (str, optional): Path to the CSV file. If None, uses default path.
        """
        if data_path is None:
            data_path = Path(__file__).parent / "data.csv"
        self.data_path = Path(data_path)
        self._data = None

    @property
    def data(self) -> pd.DataFrame:
        """Lazy load the benchmark data."""
        if self._data is None:
            self._data = pd.read_csv(self.data_path)
        return self._data

    def get_news_by_id(self, news_id: int) -> Dict:
        """Get a specific news entry by its ID.

        Args:
            news_id (int): The ID of the news entry to retrieve.

        Returns:
            dict: News entry as a dictionary
        """
        news = self.data[self.data["id"] == news_id].iloc[0].to_dict()
        return news

    def get_news_by_symbol(self, symbol: str) -> List[Dict]:
        """Get all news entries related to a specific symbol.

        Args:
            symbol (str): Stock/crypto symbol to search for

        Returns:
            List[dict]: List of news entries containing the symbol
        """
        # Filter rows where related_symbols contains the symbol
        mask = self.data["related_symbols"].fillna("").str.contains(symbol, case=False)
        news_list = self.data[mask].to_dict("records")
        return news_list

    def get_news_by_impact(self, impact: str) -> List[Dict]:
        """Get all news entries with a specific impact.

        Args:
            impact (str): Impact type ('positive', 'negative', or 'neutral')

        Returns:
            List[dict]: List of news entries with the specified impact
        """
        news_list = self.data[self.data["impact"] == impact].to_dict("records")
        return news_list

    def get_all_symbols(self) -> List[str]:
        """Get a list of all unique symbols in the dataset.

        Returns:
            List[str]: List of unique symbols
        """
        # Combine all symbols and split them
        all_symbols = self.data["related_symbols"].dropna().str.split(";").sum()
        # Return unique symbols
        return list(set(all_symbols))


if __name__ == "__main__":
    loader = BenchmarkDataLoader()
    print(loader.data.related_symbols.unique())
    print(loader.get_all_symbols())
