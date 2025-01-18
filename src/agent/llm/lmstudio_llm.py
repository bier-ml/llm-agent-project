import inspect
import os
import re
from typing import Any, Dict, List, Optional

import aiohttp

from src.agent.llm.base_llm import BaseLLMProcessor
from src.agent.planning.prompts.code_action_prompt import CODE_ACTION_SYSTEM_PROMPT
from src.common.interfaces import Message


class LMStudioProcessor(BaseLLMProcessor):
    def __init__(self, mock_functions: Optional[List[callable]] = None):
        """
        Initialize LMStudio processor.

        Args:
            mock_functions (Optional[List[callable]]): List of mock functions to use for parameter parsing.
                If None, no function parameter mapping will be attempted.
        """
        self.base_url = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1")
        self.system_prompt = CODE_ACTION_SYSTEM_PROMPT
        self.mock_functions = mock_functions or []

    async def _create_chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Create a chat completion using LM Studio's API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json={
                        "messages": messages,
                        "temperature": temperature,
                        "stream": False,
                    },
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API returned status code {response.status}")

                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Error in LM Studio processing: {str(e)}")

    def _format_message_history(self, message: Message, chat_history: Optional[list] = None) -> List[Dict[str, str]]:
        """Format the message and chat history for the LLM."""
        messages = [{"role": "system", "content": self.system_prompt}]

        if chat_history:
            messages.extend(chat_history)

        messages.append({"role": "user", "content": message.content})
        return messages

    def _parse_action_block(self, content: str) -> Dict[str, Any]:
        """Parse the action block to extract function name and parameters."""
        try:
            # Find content between Action: and End Action
            action_match = re.search(r"Action:\s*(.*?)\s*End Action", content, re.DOTALL)
            if not action_match:
                return {}

            action_code = action_match.group(1).strip()

            # Extract function call using regex
            func_match = re.search(r"(\w+)\((.*?)\)", action_code)
            if not func_match:
                return {}

            function_name = func_match.group(1)
            params_str = func_match.group(2)

            # Parse parameters
            params = {}
            if params_str:
                # Split by comma, but not within quotes
                param_parts = re.findall(r"""(?:[^,"]|"(?:\\.|[^"])*")+""", params_str)

                # Get function signature if available
                param_names = []
                for func in self.mock_functions:
                    if func.__name__ == function_name:
                        sig = inspect.signature(func)
                        param_names = list(sig.parameters.keys())
                        break

                for i, part in enumerate(param_parts):
                    part = part.strip()

                    # Handle named parameters (key=value)
                    if "=" in part:
                        key, value = part.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                    else:
                        # Positional parameter
                        if i < len(param_names):
                            key = param_names[i]
                        else:
                            # If no parameter name mapping available, use index as key
                            key = f"param_{i}"
                        value = part

                    # Clean up value
                    value = value.strip("\"'")

                    # Convert to appropriate type
                    try:
                        if value.isdigit():
                            value = int(value)
                        elif value.replace(".", "").isdigit() and value.count(".") == 1:
                            value = float(value)
                    except (ValueError, AttributeError):
                        pass

                    params[key] = value

            return {"function_name": function_name, "function_params": params}
        except Exception:
            return {}

    async def process_message(self, message: Message) -> Dict[str, Any]:
        """Process a message and return a response with structured function calls."""
        try:
            messages = self._format_message_history(message)
            response_content = await self._create_chat_completion(messages)

            # Parse the action block
            parsed_action = self._parse_action_block(response_content)

            return {
                "message": response_content,
                "thought": self._extract_thought(response_content),
                "function": parsed_action,
            }
        except Exception as e:
            return {
                "message": f"I apologize, but I encountered an error: {str(e)}",
                "thought": None,
                "function": None,
            }

    def _extract_thought(self, content: str) -> Optional[str]:
        """Extract the thought from the response content."""
        thought_match = re.search(r"Thought:(.*?)(?:Action:|Answer:)", content, re.DOTALL)
        if thought_match:
            return thought_match.group(1).strip()
        return None
