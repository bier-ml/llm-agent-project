import json
from abc import ABC, abstractmethod
from typing import Any, Literal

import openai
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

class BaseLLMModel(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def invoke(self, request: str) -> Any:
        pass


class CheckPrice(BaseModel):
    stock_name: str


class ReturnOutput(BaseModel):
    output: str


class OpenAILLMModel(BaseLLMModel):

    def __init__(self):
        super().__init__()
        self.client = OpenAI()
        self.model_name = "gpt-4o"

    def invoke(self, chat: list) -> Any:
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=chat,
            tools=[openai.pydantic_function_tool(CheckPrice), openai.pydantic_function_tool(ReturnOutput)],
            tool_choice="required"
        ).choices[0].message


if __name__ == '__main__':
    model = OpenAILLMModel()
    initial_request = "How much apple stocks I can buy on 100$?"
    messages = [{"role": "user", "content": initial_request}]
    import json

    for i in range(5):
        output = model.invoke(messages)
        messages.append(dict(output))
        print(dict(output))
        print(messages[-1]["tool_calls"][0].id)
        request = input()
        tool_call = {
            "role": "tool",
            "content": json.dumps({
                "output": request,
            }),
            # Here we specify the tool_call_id that this result corresponds to
            "tool_call_id": messages[-1]["tool_calls"][0].id
        }
        messages.append(tool_call)
        print(messages)

