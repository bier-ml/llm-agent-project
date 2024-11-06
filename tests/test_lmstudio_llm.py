import pytest

from src.agent.llm.lmstudio_llm import LMStudioProcessor
from src.agent.planning.prompts.mock_functions import MOCK_FUNCTIONS
from src.common.interfaces import Message


def some_function(symbol: str, price: int, rate: float):
    """Test mock function"""
    pass


def analyze_news(symbol: str, days: int = 7):
    """Test mock function"""
    pass


TEST_MOCK_FUNCTIONS = [some_function, analyze_news]


@pytest.fixture
def lm_processor():
    return LMStudioProcessor(mock_functions=MOCK_FUNCTIONS)


def test_parse_simple_action():
    processor = LMStudioProcessor(mock_functions=MOCK_FUNCTIONS)

    response = """
    Thought: I should check the stock price
    Action:
    get_stock_price("AAPL")
    End Action
    """

    parsed = processor._parse_action_block(response)
    assert parsed == {
        "function_name": "get_stock_price",
        "function_params": {"symbol": "AAPL"},
    }


def test_parse_action_with_multiple_params():
    processor = LMStudioProcessor(mock_functions=TEST_MOCK_FUNCTIONS)

    response = """
    Thought: I need to analyze recent news
    Action:
    analyze_news("AAPL", days=7)
    End Action
    """

    parsed = processor._parse_action_block(response)
    assert parsed == {
        "function_name": "analyze_news",
        "function_params": {"symbol": "AAPL", "days": 7},
    }


def test_extract_thought():
    processor = LMStudioProcessor()  # No mock functions needed for this test

    response = """
    Thought: This is my analysis
    Action:
    get_stock_price("AAPL")
    End Action
    """

    thought = processor._extract_thought(response)
    assert thought == "This is my analysis"


def test_parse_invalid_action():
    processor = LMStudioProcessor()  # No mock functions needed for this test

    response = """
    Thought: Something
    Action:
    invalid_syntax(
    End Action
    """

    parsed = processor._parse_action_block(response)
    assert parsed == {}


def test_parse_no_action():
    processor = LMStudioProcessor()  # No mock functions needed for this test

    response = """
    Answer: This is just an answer with no action.
    """

    parsed = processor._parse_action_block(response)
    assert parsed == {}


@pytest.mark.asyncio
async def test_process_message_full_response():
    processor = LMStudioProcessor(mock_functions=MOCK_FUNCTIONS)

    # Mock the _create_chat_completion method
    async def mock_completion(*args, **kwargs):
        return """
        Thought: I should analyze the market
        Action:
        get_market_analysis("AAPL")
        End Action
        """

    processor._create_chat_completion = mock_completion

    message = Message(content="What's happening with AAPL?")
    result = await processor.process_message(message)

    assert result["thought"] == "I should analyze the market"
    assert result["function"] == {
        "function_name": "get_market_analysis",
        "function_params": {"symbol": "AAPL"},
    }


def test_parse_action_with_numeric_params():
    processor = LMStudioProcessor(mock_functions=TEST_MOCK_FUNCTIONS)

    response = """
    Thought: Testing numeric parameters
    Action:
    some_function("AAPL", 42, 3.14)
    End Action
    """

    parsed = processor._parse_action_block(response)
    assert parsed["function_params"].get("price", None) == 42
    assert parsed["function_params"].get("rate", None) == 3.14


def test_extract_thought_with_answer():
    processor = LMStudioProcessor()  # No mock functions needed for this test

    response = """
    Thought: Initial analysis
    Action:
    get_stock_price("AAPL")
    End Action
    
    Observation: Price is $150
    
    Thought: Final conclusion
    Answer: The stock looks good
    """

    thought = processor._extract_thought(response)
    assert thought == "Initial analysis"
