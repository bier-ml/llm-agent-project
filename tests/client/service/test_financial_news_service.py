import pytest
from unittest.mock import Mock, patch
from newsapi.newsapi_exception import NewsAPIException
from src.client.service.financial_news_service import FinancialNewsService


@pytest.fixture
def mock_news_api():
    with patch('newsapi.NewsApiClient') as mock:
        yield mock


@pytest.fixture
def sample_articles():
    return {
        "status": "ok",
        "articles": [
            {
                "title": "Test Article 1",
                "description": "Description 1",
                "content": "Content 1",
                "url": "http://test1.com"
            },
            {
                "title": "Test Article 2",
                "description": "Description 2",
                "content": "Content 2",
                "url": "http://test2.com"
            }
        ]
    }


@patch.dict('os.environ', {'NEWSAPI_KEY': 'test_key'})
@patch('newsapi.NewsApiClient')
def test_init_success(mock_news_api):
    service = FinancialNewsService()
    assert service.api is not None


@patch('newsapi.NewsApiClient')
def test_init_missing_api_key(mock_news_api):
    # Ensure we're starting with a clean environment
    with patch.dict('os.environ', {}, clear=True):
        # Mock dotenv.load_dotenv to do nothing
        with patch('dotenv.load_dotenv', return_value=None):
            with pytest.raises(ValueError) as exc_info:
                FinancialNewsService()
            assert "NEWSAPI_KEY environment variable is not set" in str(
                exc_info.value)


@patch.dict('os.environ', {'NEWSAPI_KEY': 'test_key'})
@patch('newsapi.NewsApiClient')
def test_get_financial_news_success(mock_news_api_class):
    mock_instance = mock_news_api_class.return_value
    mock_instance.get_everything.return_value = {
        "status": "ok",
        "articles": [
            {"title": "Test Article 1", "description": "Description 1",
                "content": "Content 1", "url": "http://test1.com"},
            {"title": "Test Article 2", "description": "Description 2",
                "content": "Content 2", "url": "http://test2.com"},
        ]
    }

    service = FinancialNewsService()
    articles = service.get_financial_news(keywords="test", page_size=2)

    assert len(articles) == 2
    assert articles[0]["title"] == "Test Article 1"
    assert articles[1]["title"] == "Test Article 2"
    mock_instance.get_everything.assert_called_once_with(
        q="test", language="en", sort_by="relevancy", page_size=2
    )


@patch.dict('os.environ', {'NEWSAPI_KEY': 'test_key'})
@patch('newsapi.NewsApiClient')
def test_get_financial_news_error(mock_news_api_class):
    # Configure the mock to raise an exception
    mock_instance = mock_news_api_class.return_value
    mock_instance.get_everything.side_effect = NewsAPIException("API Error")

    service = FinancialNewsService()
    articles = service.get_financial_news()

    assert articles == []


@patch.dict('os.environ', {'NEWSAPI_KEY': 'test_key'})
@patch('newsapi.NewsApiClient')
def test_print_news(mock_news_api_class, sample_articles):
    service = FinancialNewsService()
    output = service.print_news(sample_articles["articles"])

    assert "Test Article 1" in output
    assert "Description 1" in output
    assert "Content 1" in output
    assert "Test Article 2" in output
    assert "Description 2" in output
    assert "Content 2" in output
