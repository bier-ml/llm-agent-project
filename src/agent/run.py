from typing import Dict, Optional

from fastapi import FastAPI, HTTPException

from src.agent.llm.base_llm import BaseLLMProcessor
from src.agent.llm.dummy_llm import DummyStockProcessor
from src.agent.llm.lmstudio_llm import LMStudioProcessor
from src.common.interfaces import Message

app = FastAPI()

# LLM processor registry
llm_processors: Dict[str, BaseLLMProcessor] = {
    "dummy": DummyStockProcessor(),
    "lmstudio": LMStudioProcessor(),
}


def get_llm_processor(llm_type: Optional[str] = None) -> BaseLLMProcessor:
    """Get the appropriate LLM processor based on type."""
    if not llm_type or llm_type not in llm_processors:
        return llm_processors["dummy"]  # Default to dummy processor
    return llm_processors[llm_type]


@app.post("/process")
async def process_message(message: Message):
    try:
        processor = get_llm_processor(message.llm_type)
        result = await processor.process_message(message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/available-llms")
async def get_available_llms():
    """Get list of available LLM processors."""
    return {"available_llms": list(llm_processors.keys())}
