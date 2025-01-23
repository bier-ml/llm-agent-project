import logging
import os

from dotenv import load_dotenv
from newsapi import NewsApiClient

logger = logging.getLogger(__name__)


class FinancialNewsService:
    """
    A service class for fetching financial news using NewsAPI.

    This service provides methods to retrieve and format news articles related to
    stocks, cryptocurrencies, and other financial topics.
    """

    def __init__(self):
        """
        Initialize the FinancialNewsService.

        Raises:
            ValueError: If NEWSAPI_KEY environment variable is not set.
        """
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
        """
        Fetch financial news articles based on specified criteria.

        Args:
            keywords (str): Search keywords for filtering news. Defaults to "stock OR crypto".
            language (str): Language of the news articles. Defaults to "en" (English).
            sort_by (str): Sorting criteria for articles. Options: 'relevancy', 'popularity', 'publishedAt'.
                          Defaults to "relevancy".
            page_size (int): Number of articles to retrieve. Defaults to 5.

        Returns:
            list: A list of dictionaries containing news articles. Each article has 'title',
                 'description', 'content', and other metadata. Returns empty list if there's an error.
        """
        logger.info(f"Fetching financial news with keywords: {keywords}")
        try:
            response = self.api.get_everything(q=keywords, language=language, sort_by=sort_by, page_size=page_size)

            if response and isinstance(response, dict):
                if response.get("status") == "ok" and "articles" in response:
                    logger.info(f"Successfully fetched {len(response['articles'])} news articles")
                    return response["articles"]
                else:
                    logger.error(f"Error in API response: {response}")
            else:
                logger.error(f"Invalid response format: {response}")
            return []
        except Exception as e:
            logger.error(f"An error occurred while fetching news: {str(e)}")
            return []

    def print_news(self, articles):
        """
        Print the list of news articles and return the output as a string.

        Args:
            articles (list): List of news articles with title, description, and url.

        Returns:
            str: Formatted string containing all articles with titles, descriptions, and content.
        """
        output = []  # Initialize a list to collect output strings
        for idx, article in enumerate(articles, start=1):
            output.append(f"{idx}. {article['title']}")
            output.append(f"   {article['description']}")
            output.append(f"   Content: {article['content']}")
            output.append("-" * 80)

        print("\n".join(output))  # Print the collected output
        return "\n".join(output)  # Return the output as a single string


# Usage Example
if __name__ == "__main__":
    load_dotenv()

    # Initialize the FinancialNewsClient with the API key
    news_client = FinancialNewsService()

    # Fetch news about stock or crypto
    financial_news = news_client.get_financial_news(page_size=100)

    # Print the news articles
    news_client.print_news(financial_news)

    print(financial_news)
