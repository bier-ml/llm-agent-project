import pytest
from fastapi.testclient import TestClient

from src.agent.run import app

client = TestClient(app)


def test_dummy_processor_default():
    """Test dummy processor when no llm_type is specified"""
    response = client.post("/process", json={"content": "Hello", "user_id": "test_user"})

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "message" in data
    assert "thought" in data
    assert "function" in data

    # Check function call details
    function_data = data["function"]
    assert function_data["function_name"] == "response_to_user"
    assert "function_params" in function_data
    assert "message" in function_data["function_params"]

    # Verify stock-related content
    assert "stocks" in function_data["function_params"]["message"].lower()
    assert "market" in function_data["function_params"]["message"].lower()


def test_dummy_processor_explicit():
    """Test dummy processor when explicitly requested"""
    response = client.post(
        "/process",
        json={"content": "Hello", "user_id": "test_user", "llm_type": "dummy"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify thought content
    assert "market conditions" in data["thought"].lower()
    assert "investing" in data["thought"].lower()


def test_available_llms():
    """Test the available-llms endpoint"""
    response = client.get("/available-llms")

    assert response.status_code == 200
    data = response.json()

    assert "available_llms" in data
    assert "dummy" in data["available_llms"]
    assert "lmstudio" in data["available_llms"]


def test_invalid_llm_type():
    """Test that invalid llm_type falls back to dummy processor"""
    response = client.post(
        "/process",
        json={
            "content": "Hello",
            "user_id": "test_user",
            "llm_type": "nonexistent_llm",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Should still get dummy processor response
    assert "stocks" in data["function"]["function_params"]["message"].lower()


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in the process endpoint"""
    # Send invalid JSON to trigger an error
    response = client.post(
        "/process",
        json={"invalid": "data"},  # Missing required fields
    )

    assert response.status_code == 422  # Validation error
