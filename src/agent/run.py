"""
FastAPI server that handles LLM processing requests. This module provides endpoints
for processing messages through different LLM processors and retrieving available LLM types.
"""

from typing import Dict, Optional

from fastapi import FastAPI, HTTPException

from src.agent.llm.base_llm import BaseLLMProcessor
from src.agent.llm.dummy_llm import DummyStockProcessor
from src.agent.llm.json_llm import JsonProcessor
from src.agent.llm.lmstudio_llm import LMStudioProcessor
from src.common.interfaces import Message

app = FastAPI()

# Registry mapping LLM types to their processor implementations
llm_processors: Dict[str, BaseLLMProcessor] = {
    "dummy": DummyStockProcessor(),
    "lmstudio": LMStudioProcessor(),
    "jsonBasedLLM": JsonProcessor(),
}


def get_llm_processor(llm_type: Optional[str] = None) -> BaseLLMProcessor:
    """
    Get the appropriate LLM processor based on type.

    Args:
        llm_type: The type of LLM processor to retrieve

    Returns:
        BaseLLMProcessor: The requested processor or dummy processor if type not found
    """
    if not llm_type or llm_type not in llm_processors:
        return llm_processors["dummy"]
    return llm_processors[llm_type]


@app.post("/process")
async def process_message(message: Message):
    """
    Process an incoming message using the specified LLM processor.

    Args:
        message: The Message object containing content and metadata

    Returns:
        The processed result from the LLM

    Raises:
        HTTPException: If processing fails
    """
    try:
        processor = get_llm_processor(message.llm_type)
        result = await processor.process_message(message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/available-llms")
async def get_available_llms():
    """Get list of available LLM processor types."""
    return {"available_llms": list(llm_processors.keys())}
