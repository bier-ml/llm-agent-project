import logging
import os
import json
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

    def _format_results_message(self, results: list, original_message: str) -> str:
        """Format results into a human readable message for the agent."""
        results_text = "\n".join(
            f"- For action '{result.get('type', 'unknown')}': {result}"
            for result in results
        )

        return (
            f"I've gathered the information you requested. Here are the results:\n\n"
            f"{results_text}\n\n"
            f"Given this information, please provide a response to the user's original message: "
            f"'{original_message}'"
        )

    # TODO: move parsing to agent side
    async def process_message(self, message: Message) -> Dict[str, Any]:
        self.logger.info(f"Processing message: {message}")
        try:

            while True:
                # Get next action from agent
                response = await self.agent_connector.send_request("process", message.__dict__)
                self.logger.info(f"Received response from agent: {response}")

                if not isinstance(response, dict):
                    return {"error": "Invalid response format from agent"}

                # Extract "message" from response and remove all ` symbols
                message_content = response.get("message", "").replace(
                    "```json", "").replace("`", "")
                self.logger.info(f"Parsed message content: {message_content}")

                # Parse the message_content as JSON
                try:
                    message_content = json.loads(message_content)
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Failed to parse message content as JSON: {str(e)}")
                    return {"error": "Invalid JSON format in message content"}

                # Parse actions and thoughts from the cleaned message
                thought = message_content.get("thought", "")
                actions = message_content.get("actions", [])
                self.logger.info(
                    f"Parsed thought: {thought}, actions: {actions}")

                # If no actions or response_to_user, return the thought to user
                if not actions or (len(actions) == 1 and actions[0]["name"] == "response_to_user"):
                    # Check if the action is "response_to_user" and return its argument
                    if actions and actions[0]["name"] == "response_to_user":
                        return {"message": actions[0].get("argument", "")}
                    return {"message": thought}

                # Execute the actions and collect results
                results = []
                for action in actions:
                    tool_call = {
                        "type": action["name"],
                        **(action.get("argument", {}) if isinstance(action.get("argument"), dict) else {"coin_id": action.get("argument", "")})
                    }
                    # Log the built tool_call
                    self.logger.info(f"Built tool_call: {tool_call}")

                    result = await self.tool_handler.handle(tool_call)

                    # Log the result of the tool call
                    self.logger.info(f"Result of tool_call: {result}")

                    results.append(result)

                # Create human readable message with results
                results_message = self._format_results_message(
                    results=results,
                    original_message=message.content
                )

                # Update context with results for next iteration
                message.content = results_message

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

        # Return the message and any action results
        if isinstance(response, dict):
            if "error" in response:
                raise HTTPException(status_code=500, detail=response["error"])
            return response

        return {"error": "Invalid response format"}

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
