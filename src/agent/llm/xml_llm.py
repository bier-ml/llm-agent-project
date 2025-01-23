import logging
import os
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

import aiohttp

from src.agent.llm.base_llm import BaseLLMProcessor
from src.agent.planning.prompts.xml_prompt import XML_PROMPT
from src.common.interfaces import Message

logger = logging.getLogger(__name__)


class XmlProcessor(BaseLLMProcessor):
    def __init__(self):
        """Initialize XML format processor."""
        self.base_url = os.getenv("LLM_API_URL", "http://localhost:1234/v1")
        self.system_prompt = XML_PROMPT
        logger.info(f"Initialized XmlProcessor with base URL: {self.base_url}")

    async def _create_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.6) -> str:
        """Create a chat completion using the LLM API."""
        try:
            logger.info(f"Sending request to LLM API with temperature: {temperature}")
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "messages": messages,
                        "temperature": temperature,
                        "stream": False,
                        "max_tokens": 1024
                    },
                ) as response:
                    if response.status != 200:
                        logger.error(f"API returned non-200 status code: {response.status}")
                        raise Exception(f"API returned status code {response.status}")

                    result = await response.json()
                    logger.info("Successfully received response from LLM API")
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error in LLM processing: {str(e)}", exc_info=True)
            raise Exception(f"Error in LLM processing: {str(e)}")

    def _format_message_history(self, message: Message, chat_history: Optional[list] = None) -> List[Dict[str, str]]:
        """Format the message and chat history for the LLM."""
        messages = [{"role": "system", "content": self.system_prompt}]

        if chat_history:
            messages.extend(chat_history)
            logger.debug(f"Added {len(chat_history)} messages from chat history")

        messages.append({"role": "user", "content": message.content})
        logger.debug(f"Formatted message history with {len(messages)} total messages")
        return messages

    def _parse_action_block(self, content: str) -> Dict[str, Any]:
        """Parse the action block to extract function name and parameters from XML."""
        try:
            # Define XML code block markers
            start = "<response>"
            end = "</response>"
            
            if start in content and end in content:
                # Extract the XML block
                content = content[content.find(start):content.find(end) + len(end)]
            else:
                logger.error("No XML block found in the content")
                return {
                    "thought": "I apologize, but I couldn't parse the response format correctly. No XML block found.",
                    "actions": [],
                }
            
            try:
                # Parse the XML content
                root = ET.fromstring(content)
                thought = root.find("thought").text if root.find("thought") is not None else ""
                actions = []
                
                for action in root.findall("actions/action"):
                    name = action.find("name").text if action.find("name") is not None else ""
                    argument = action.find("argument").text if action.find("argument") is not None else None
                    action_data = {"name": name}
                    if argument:
                        action_data["argument"] = argument
                    actions.append(action_data)
                
                return {
                    "thought": thought,
                    "actions": actions,
                }
            except ET.ParseError as e:
                logger.error(f"Failed to parse XML content: {str(e)}")
                return {
                    "thought": f"I apologize, but I couldn't parse the response format correctly. XML parsing error: {str(e)}",
                    "actions": [],
                }
        except Exception as e:
            logger.error(f"Failed to parse XML content: {str(e)}")
            return {
                "thought": "I apologize, but I couldn't parse the response format correctly. Exception occurred.",
                "actions": [],
            }

    def _extract_thought(self, content: str) -> Optional[str]:
        """Extract the thought process from the response content."""
        try:
            parsed_content = self._parse_action_block(content)
            return parsed_content.get("thought")
        except Exception as e:
            logger.error(f"Error extracting thought: {str(e)}")
            return None

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Process a message and return the LLM's response."""
        try:
            logger.info(f"Processing message: {message.content[:50]}...")
            messages = self._format_message_history(message)
            response = await self._create_chat_completion(messages)
            logger.debug("Successfully received completion from LLM")

            # Parse the response and extract thought and actions
            parsed_response = self._parse_action_block(response)

            return parsed_response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return {"thought": f"Error in LLM processing: {str(e)}", "actions": []}
