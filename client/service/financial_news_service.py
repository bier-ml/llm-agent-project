import os

from newsapi import NewsApiClient
from dotenv import load_dotenv

class FinancialNewsService:
    def __init__(self, api_key):
        self.api = NewsApiClient(api_key=api_key)

    def get_financial_news(self, keywords='stock OR crypto', language='en', sort_by='relevancy', page_size=5):
        """
        Fetch financial news using the NewsAPI 'everything' endpoint.

        Args:
        - keywords: str, Keywords related to finance like 'stock', 'crypto', etc.
        - language: str, Language of the news articles. Default is 'en' for English.
        - sort_by: str, Sorting method for news articles ('relevancy', 'popularity', 'publishedAt').
        - page_size: int, The number of news articles to return.

        Returns:
        - List of news articles containing title, description, and url.
        """
        try:
            response = self.api.get_everything(
                q=keywords,
                language=language,
                sort_by=sort_by,
                page_size=page_size
            )

            if response['status'] == 'ok':
                return response['articles']
            else:
                print(f"Error fetching news: {response['status']}")
                return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def print_news(self, articles):
        """
        Print the list of news articles.

        Args:
        - articles: List of news articles with title, description, and url.
        """
        for idx, article in enumerate(articles, start=1):
            print(f"{idx}. {article['title']}")
            print(f"   {article['description']}")
            print(f"   Content: {article['content']}")
            print('-' * 80)

# Usage Example
if __name__ == "__main__":
    load_dotenv()

    # Your NewsAPI key here
    api_key = os.getenv('NEWSAPI_KEY')

    # Initialize the FinancialNewsClient with the API key
    news_client = FinancialNewsService(api_key=api_key)

    # Fetch news about stock or crypto
    financial_news = news_client.get_financial_news(page_size=100)

    # Print the news articles
    news_client.print_news(financial_news)
