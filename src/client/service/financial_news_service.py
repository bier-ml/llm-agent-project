import logging
import os

from dotenv import load_dotenv
from newsapi import NewsApiClient

logger = logging.getLogger(__name__)

class FinancialNewsService:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            logger.error("NEWSAPI_KEY environment variable is not set")
            raise ValueError("NEWSAPI_KEY environment variable is not set")
        self.api = NewsApiClient(api_key=api_key)
        logger.info("FinancialNewsService initialized successfully")

    def get_financial_news(
        self,
        keywords="stock OR crypto",
        language="en",
        sort_by="relevancy",
        page_size=5,
    ):
        logger.info(f"Fetching financial news with keywords: {keywords}")
        try:
            response = self.api.get_everything(
                q=keywords, language=language, sort_by=sort_by, page_size=page_size
            )

            if response["status"] == "ok":
                logger.info(f"Successfully fetched {len(response['articles'])} news articles")
                return response["articles"]
            else:
                logger.error(f"Error fetching news: {response['status']}")
                return []
        except Exception as e:
            logger.error(f"An error occurred while fetching news: {e}")
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
            print("-" * 80)


# Usage Example
if __name__ == "__main__":
    load_dotenv()

    # Initialize the FinancialNewsClient with the API key
    news_client = FinancialNewsService()

    # Fetch news about stock or crypto
    financial_news = news_client.get_financial_news(page_size=100)

    # Print the news articles
    news_client.print_news(financial_news)
