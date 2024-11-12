import logging
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from src.client.services import AgentServiceConnector, ToolCallHandler
from src.common.interfaces import Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


class ClientService:
    def __init__(self):
        self.agent_connector = AgentServiceConnector(
            base_url=os.getenv("AGENT_SERVICE_URL", "http://agent:8001")
        )
        self.tool_handler = ToolCallHandler()
        self.logger = logging.getLogger(__name__)

    async def process_message(self, message: Message) -> Dict[str, Any]:
        self.logger.info(f"Processing message: {message}")
        try:
            response = await self.agent_connector.send_request("process", message.__dict__)
            self.logger.info(f"Received response from agent: {response}")
            
            # Handle parsed function calls from agent
            if response.get("function"):
                function_data = response["function"]
                self.logger.debug(f"Parsed function data: {function_data}")
                tool_call = {
                    "type": function_data["function_name"],  # Convert function_name to type
                    **function_data["function_params"]  # Spread other parameters
                }
                self.logger.debug(f"Converted tool call: {tool_call}")
                
                result = await self.tool_handler.handle(tool_call)
                return {
                    "message": response["message"],
                    "result": result
                }
                
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise


client_service = ClientService()


@app.post("/process_message")
async def process_message(message: Message):
    logger.info(f"Received message processing request: {message}")
    try:
        message.llm_type = "lmstudio"
        
        response = await client_service.process_message(message)
        logger.info(f"Successfully processed message: {response}")
        
        # Return appropriate message based on response structure
        if isinstance(response, dict) and "message" in response:
            return {"message": response["message"]}
        return response
        
    except TimeoutError as e:
        error_msg = "The LLM service is taking too long to respond. Please try again later."
        logger.error(f"{error_msg} Original error: {str(e)}")
        raise HTTPException(status_code=504, detail=error_msg)
        
    except Exception as e:
        error_msg = "An error occurred while processing your message"
        logger.error(f"{error_msg}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/tool_call")
async def handle_tool_call(tool_call: Dict[str, Any]):
    logger.info(f"Received tool call request: {tool_call}")
    try:
        result = await client_service.tool_handler.handle(tool_call)
        logger.info(f"Successfully handled tool call: {result}")
        return result
    except Exception as e:
        logger.error(f"Error handling tool call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
