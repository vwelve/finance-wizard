from typing import List, Dict, Any, Callable, Union
import json

from util.exceptions import ToolFunctionError
from util.search_web import search_web

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

# Define a type for the available functions dictionary
AvailableFunctions = Dict[str, Callable[[str], Union[str, Any]]]

# Define available functions
available_functions: AvailableFunctions = {
    "search_web": search_web
}


class ToolCall:
    def __init__(self, _id: int, function: 'Function'):
        self.id = _id
        self.function = function


class Function:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


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
        function_name = tool_call["function"]["name"]
        function_to_call = available_functions.get(function_name)

        if function_to_call:
            function_args = json.loads(tool_call["function"]["arguments"])

            try:
                function_response = await function_to_call(
                    prompt=function_args.get("prompt")
                )
            except Exception as e:
                raise ToolFunctionError(function_name, e)

            tool_responses.append(
                {
                    "tool_call_id": tool_call["id"],
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

    return tool_responses
