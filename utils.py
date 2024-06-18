import json
import tiktoken
from typing import List, Dict, Any, Callable, Union

from exceptions import ToolFunctionError
from search_web import search_web

# Define a type for the available functions dictionary
AvailableFunctions = Dict[str, Callable[[str], Union[str, Any]]]

# Define available functions
available_functions: AvailableFunctions = {
    "search_web": search_web
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "If a user requests data on a stock I don't have, I'll search a link like ["
                           "https://finance.yahoo.com/quote/TICKER/history?p=TICKER] or from trading view like ["
                           "https://www.tradingview.com/symbols/SYMBOL]",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The URL or information you want to with the format of ["
                                       "https://finance.yahoo.com/quote/TICKER/history?p=TICKER] or "
                                       "[https://www.tradingview.com/symbols/SYMBOL]",
                    },
                },
                "required": ["prompt"],
            },
        },
    }
]


class ToolCall:
    def __init__(self, id: int, function: 'Function'):
        self.id = id
        self.function = function


class Function:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


def count_tokens(messages: List[dict], model="gpt-4o-2024-05-13"):
    """
    Calculate the total number of tokens used by a list of messages for a given model.

    Args:
        messages (List[dict]): A list of messages, where each message is a dictionary with 'role' and 'content' keys.
        model (str): The model name to be used for encoding the messages. Default is "gpt-4-turbo-2024-04-09".

    Returns:
        int: The total number of tokens used by the messages.
    """
    encoder = tiktoken.encoding_for_model(model)
    return 0
    """# Calculate the number of tokens in each message and the total number of tokens
    total_tokens = 0
    for message in messages:
        content_tokens = encoder.encode(message['content'])
        num_content_tokens = len(content_tokens)

        # Add extra tokens for the role and any necessary separators
        # This is a rough approximation; actual token usage may vary slightly
        num_tokens = num_content_tokens + 4  # Adding 4 for the role and separators
        total_tokens += num_tokens

    return total_tokens"""


async def handle_tools(tool_calls: List[ToolCall]) -> List[Dict[str, Any]]:
    """
    Handle OpenAI tool calls by invoking the appropriate functions and collecting their responses.

    Args:
        tool_calls (List[ToolCall]): A list of tool call objects, each containing a function name and arguments.
        available_functions (AvailableFunctions): A dictionary mapping function names to callable functions.

    Returns:
        List[Dict[str, Any]]: A list of messages with the results of the tool calls.
    """
    tool_responses = []

    for tool_call in tool_calls:
        # Extract function name from the tool call
        function_name = tool_call.function.name

        # Get the corresponding function from the available functions dictionary
        function_to_call = available_functions.get(function_name)

        if function_to_call:
            # Parse the function arguments
            function_args = json.loads(tool_call.function.arguments)

            try:
                # Call the function with the provided arguments
                function_response = await function_to_call(
                    prompt=function_args.get("prompt")
                )
            except:
                raise ToolFunctionError(function_name)

            # Append the response to the messages list
            tool_responses.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

    return tool_responses
