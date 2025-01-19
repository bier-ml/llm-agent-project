from unittest.mock import MagicMock, patch

import pytest
from newsapi.newsapi_exception import NewsAPIException

from src.client.service.financial_news_service import FinancialNewsService


# Mock dotenv.load_dotenv at the module level for all tests
@pytest.fixture(autouse=True)
def mock_dotenv():
    with patch("dotenv.load_dotenv", return_value=True):
        yield


@pytest.fixture
def mock_news_api(sample_articles):
    with patch("newsapi.NewsApiClient") as mock_class:
        mock_instance = MagicMock()
        # Configure the mock with default successful response
        mock_instance.get_everything.return_value = sample_articles
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_articles():
    return {
        "status": "ok",
        "articles": [
            {
                "title": "Test Article 1",
                "description": "Description 1",
                "content": "Content 1",
                "url": "http://test1.com",
            },
            {
                "title": "Test Article 2",
                "description": "Description 2",
                "content": "Content 2",
                "url": "http://test2.com",
            },
        ],
    }


def test_init_success():
    with patch("os.getenv", return_value="test_key"):
        service = FinancialNewsService()
        assert service.api is not None


def test_init_missing_api_key():
    with patch.dict("os.environ", {}, clear=True):
        with patch("os.getenv", return_value=None):
            with pytest.raises(ValueError) as exc_info:
                FinancialNewsService()
            assert "NEWSAPI_KEY environment variable is not set" in str(exc_info.value)


# def test_get_financial_news_success(mock_news_api, sample_articles):
#     with patch("os.getenv", return_value="test_key"):
#         service = FinancialNewsService()
#         articles = service.get_financial_news(keywords="test", page_size=2)

#         assert len(articles) == 2
#         assert articles[0]["title"] == "Test Article 1"
#         assert articles[1]["title"] == "Test Article 2"
#         mock_news_api.get_everything.assert_called_once_with(
#             q="test",
#             language="en",
#             sort_by="relevancy",
#             page_size=2
#         )


# def test_get_financial_news_failed_status(mock_news_api):
#     with patch("os.getenv", return_value="test_key"):
#         # Override the default mock response for this specific test
#         mock_news_api.get_everything.return_value = {
#             "status": "error",
#             "code": "apiKeyInvalid"
#         }

#         service = FinancialNewsService()
#         articles = service.get_financial_news(keywords="test", page_size=2)

#         assert articles == []
#         mock_news_api.get_everything.assert_called_once_with(
#             q="test",
#             language="en",
#             sort_by="relevancy",
#             page_size=2
#         )


def test_get_financial_news_error(mock_news_api):
    with patch("os.getenv", return_value="test_key"):
        # Configure the mock instance before creating the service
        mock_news_api.get_everything.side_effect = NewsAPIException("API Error")

        service = FinancialNewsService()
        articles = service.get_financial_news()

        assert articles == []


def test_print_news(mock_news_api, sample_articles):
    with patch("os.getenv", return_value="test_key"):
        service = FinancialNewsService()
        output = service.print_news(sample_articles["articles"])

        assert "Test Article 1" in output
        assert "Description 1" in output
        assert "Content 1" in output
        assert "Test Article 2" in output
        assert "Description 2" in output
        assert "Content 2" in output
