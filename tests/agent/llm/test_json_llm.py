import pytest
from unittest.mock import patch, AsyncMock
import json

from src.agent.llm.json_llm import JsonProcessor
from src.common.interfaces import Message


@pytest.fixture
def json_processor():
    return JsonProcessor()


@pytest.mark.asyncio
async def test_create_chat_completion_success(json_processor):
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": """```json
                    {
                        "thought": "Test thought",
                        "actions": [{"action": "test_action"}]
                    }
                    ```"""
                }
            }
        ]
    }

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value.status = 200
        mock_context.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        mock_post.return_value = mock_context

        result = await json_processor._create_chat_completion([{"role": "user", "content": "test"}])

        assert "thought" in result
        assert "actions" in result


@pytest.mark.asyncio
async def test_create_chat_completion_api_error(json_processor):
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value.status = 500
        mock_post.return_value = mock_context

        with pytest.raises(Exception) as exc_info:
            await json_processor._create_chat_completion([{"role": "user", "content": "test"}])

        assert "API returned status code 500" in str(exc_info.value)


def test_format_message_history_no_chat_history(json_processor):
    message = Message(content="test message", user_id="test_user")
    formatted = json_processor._format_message_history(message)

    assert len(formatted) == 2  # System prompt + user message
    assert formatted[0]["role"] == "system"
    assert formatted[1]["role"] == "user"
    assert formatted[1]["content"] == "test message"


def test_format_message_history_with_chat_history(json_processor):
    message = Message(content="test message", user_id="test_user")
    chat_history = [
        {"role": "user", "content": "previous message"},
        {"role": "assistant", "content": "previous response"},
    ]

    formatted = json_processor._format_message_history(message, chat_history)

    assert len(formatted) == 4  # System prompt + chat history + user message
    assert formatted[1]["content"] == "previous message"
    assert formatted[2]["content"] == "previous response"


def test_parse_action_block_valid_json(json_processor):
    content = """```json
    {
        "thought": "Test thought",
        "actions": [{"action": "test_action"}]
    }
    ```"""

    result = json_processor._parse_action_block(content)

    assert result["thought"] == "Test thought"
    assert len(result["actions"]) == 1
    assert result["actions"][0]["action"] == "test_action"


def test_parse_action_block_invalid_json(json_processor):
    content = """```json
    {
        "thought": "Test thought",
        invalid json content
    }
    ```"""

    result = json_processor._parse_action_block(content)

    assert "couldn't parse" in result["thought"].lower()
    assert result["actions"] == []


def test_extract_thought_success(json_processor):
    content = """```json
    {
        "thought": "Test thought",
        "actions": []
    }
    ```"""

    thought = json_processor._extract_thought(content)

    assert thought == "Test thought"


def test_extract_thought_failure(json_processor):
    content = "Invalid content"

    thought = json_processor._extract_thought(content)

    assert "apologize" in thought


@pytest.mark.asyncio
async def test_process_message_success(json_processor):
    mock_response = """```json
    {
        "thought": "Test thought",
        "actions": [{"action": "test_action"}]
    }
    ```"""

    with patch.object(json_processor, "_create_chat_completion", new_callable=AsyncMock) as mock_completion:
        mock_completion.return_value = mock_response

        result = await json_processor.process_message(Message(content="test", user_id="test_user"))

        assert result["thought"] == "Test thought"
        assert len(result["actions"]) == 1
        assert result["actions"][0]["action"] == "test_action"


@pytest.mark.asyncio
async def test_process_message_error(json_processor):
    with patch.object(json_processor, "_create_chat_completion", new_callable=AsyncMock) as mock_completion:
        mock_completion.side_effect = Exception("Test error")

        result = await json_processor.process_message(Message(content="test", user_id="test_user"))

        assert "Error in LLM processing" in result["thought"]
        assert result["actions"] == []
