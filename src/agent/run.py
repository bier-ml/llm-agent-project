from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from src.agent.llm import LLMProcessor
from src.common.interfaces import Message, MessageProcessor

app = FastAPI()


class AgentService:
    def __init__(self):
        self.llm_processor: MessageProcessor = LLMProcessor()

    async def process_message(self, message: Message) -> Dict[str, Any]:
        return await self.llm_processor.process_message(message)


agent_service = AgentService()


@app.post("/process")
async def process_message(message: Message):
    try:
        return await agent_service.process_message(message)
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Unable to connect to LLM service")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
