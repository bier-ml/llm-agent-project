# LLM Agent Service

This service provides a FastAPI-based API for interacting with different LLM processors. Currently supports two types of processors:

-   Dummy Stock Advisor (default)
-   LMStudio Integration

# Setup

## Environment Variables:

`LMSTUDIO_API_URL=http://localhost:1234/v1` # Required for LMStudio processor

## Running with Docker:

# Build and start the service

```bash
./scripts/docker/build.sh
./scripts/docker/up.sh
```

# Stop the service

```bash
./scripts/docker/down.sh
```

# API Endpoints

## Process Message

`POST /process`

Process a message through the selected LLM processor.

### Request Body:

```json
{
    "content": "What stocks should I invest in?",
    "processor_type": "dummy" // Optional: "dummy" or "lmstudio"
}
```

### Response Format:

```json
{
    "message": "Raw response from the LLM",
    "thought": "Extracted thought process (if any)",
    "function": {
        "function_name": "name_of_function",
        "function_params": {
            "param1": "value1",
            "param2": "value2"
        }
    }
}
```

# Example Usage

```python
import requests

# Process a message using the dummy processor
response = requests.post(
    "http://localhost:8000/process",
    json={
        "content": "What stocks should I invest in?",
        "processor_type": "dummy"
    }
)

print(response.json())

# Process a message using LMStudio
response = requests.post(
    "http://localhost:8000/process",
    json={
        "content": "What stocks should I invest in?",
        "processor_type": "lmstudio"
    }
)

print(response.json())
```

# Processor Types

## Dummy Stock Advisor:

A simple processor that always returns stock investment advice. Useful for testing and development.

## LMStudio Integration:

Connects to a local LMStudio instance for more sophisticated language processing. Requires LMStudio to be running locally with the API enabled.

# Error Handling

The service returns appropriate HTTP status codes:

-   200: Successful processing
-   400: Invalid request
-   500: Server error or LLM processing error

Error responses include an error message in the response body:

```json
{
    "detail": "Error message describing what went wrong"
}
```

# Development

## Adding New Processors:

1. Create a new class that inherits from `BaseLLMProcessor`
2. Implement all required abstract methods
3. Register the processor in the service factory

## Testing:

Run the test suite:

```bash
pytest tests/
```
