"""
This module defines the prompts and formatting instructions for the code-based action system.
It provides tools for generating function descriptions and example trajectories for the AI agent.
"""

import inspect
from textwrap import dedent
from typing import List

from src.agent.planning.prompts.mock_functions import MOCK_FUNCTIONS


def generate_tool_description(functions: List[callable]) -> str:
    """
    Generates a numbered tool description format from a list of callable functions.

    Args:
        functions: List of callable functions to generate descriptions for

    Returns:
        str: A formatted string containing numbered descriptions of all tools,
             including their signatures, arguments, and docstrings
    """
    tool_descriptions = []

    for i, func in enumerate(functions, 1):
        name = func.__name__
        signature = inspect.signature(func)

        # Get args
        args = list(signature.parameters.keys())
        args_str = ", ".join(args) if args else "no arguments"

        # Get return type
        return_type = signature.return_annotation.__name__ if signature.return_annotation != inspect._empty else "Any"

        # Build description
        signature_str = f"{name}({args_str}) -> {return_type}"
        description = f"[{i}] {name}: {func.__doc__}\n"
        if args:
            description += f"Arguments: {args_str}.\n"
        description += f"Signature: {signature_str}"
        tool_descriptions.append(description)

    return "\n\n".join(tool_descriptions)


FORMATING_INSTRUCTION = dedent("""
    You can use the tools by outputing a block of Python code that invoke the tools.
    You may use for-loops, if-statements, and other Python constructs when necessary.
    Be sure to print the final answer at the end of your code.
    You should begin your tool invocation with 'Action:' and end it with 'End Action'.
    Example: 'Action:
    tool_name(argument_1)
    End Action'
                               
    You can optionally express your thoughts using natural language before your action. For
    example, 'Thought: I want to use tool_name to do something. Action: <your action to
    call tool_name> End Action'.
    Note that your output should always contain either 'Action:' or 'Answer:', but not both.
    When you are done, output the result using 'Answer: your answer'
""")
"""Instructions for the AI agent on how to format its responses and use tools."""

# Example of agent trajectory with received observations using actual function signatures
EXAMPLE_AGENT_TRAJECTORY = dedent("""
    Thought: I want to get the current price of a stock to determine the trend.
    Action:
    get_stock_price("AAPL")
    End Action

    ---

    Observation: The current price of AAPL is 100.0.

    ---

    Thought: I should analyze recent news to understand the market sentiment for AAPL.
    Action:
    analyze_news("AAPL", days=7)
    End Action

    ---

    Observation: Recent news sentiment is positive.

    ---

    Thought: The positive news sentiment suggests a bullish trend. I should get a detailed market analysis.
    Action:
    get_market_analysis("AAPL")
    End Action

    ---

    Observation: The market analysis indicates a bullish trend with support at 95.0 and resistance at 105.0.

    ---

    Thought: Based on the current price, positive news sentiment, and bullish market analysis, it is advisable to buy AAPL.
    Answer: It is advisable to buy AAPL based on the current price, positive news sentiment, and bullish market analysis.
""")
"""Example conversation showing how the agent should interact with tools and provide responses."""

# Use it in the main prompt
CODE_ACTION_SYSTEM_PROMPT_BASE = dedent("""
    You are IVAN (Interactive Venture Analysis Network), a financial advisor specializing in stocks and cryptocurrencies.
    You have access to the following tools:

    {TOOL_DESCRIPTION}

    {FORMATING_INSTRUCTION}

    Here is an example of how you might use these tools:

    {EXAMPLE_AGENT_TRAJECTORY}
""")
"""Base template for the system prompt, to be formatted with tool descriptions and instructions."""

CODE_ACTION_SYSTEM_PROMPT = CODE_ACTION_SYSTEM_PROMPT_BASE.format(
    TOOL_DESCRIPTION=generate_tool_description(MOCK_FUNCTIONS),
    FORMATING_INSTRUCTION=FORMATING_INSTRUCTION,
    EXAMPLE_AGENT_TRAJECTORY=EXAMPLE_AGENT_TRAJECTORY,
)

if __name__ == "__main__":
    print(CODE_ACTION_SYSTEM_PROMPT)
