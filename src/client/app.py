import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from src.client.services import AgentServiceConnector, ToolCallHandler
from src.common.interfaces import Message, MessageProcessor

app = FastAPI()


class ClientService:
    def __init__(self):
        self.agent_connector = AgentServiceConnector(
            base_url=os.getenv("AGENT_SERVICE_URL", "http://agent:8001")
        )
        self.tool_handler = ToolCallHandler()

    async def process_message(self, message: Message) -> Dict[str, Any]:
        return await self.agent_connector.send_request("process", message.__dict__)


client_service = ClientService()


@app.post("/process_message")
async def process_message(message: Message):
    try:
        response = await client_service.process_message(message)
        return {"message": response["message"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool_call")
async def handle_tool_call(tool_call: Dict[str, Any]):
    return await client_service.tool_handler.handle(tool_call)
