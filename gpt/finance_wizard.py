import logging
import uuid

from openai import AsyncOpenAI

from typing import List, AsyncGenerator, Any, Dict

from gpt.tools import handle_tools, TOOLS
from db.database import Database

MAX_TOTAL_TOKENS = 32768


class FinanceWizard:
    def __init__(self, uid: str, token: str):
        self.uid = str(uid)
        self.client = AsyncOpenAI(api_key=token)

    def get_message_history(self) -> List[Dict[str, Any]]:
        rows = Database.get_user_messages(self.uid)
        message_history = []

        if len(rows) == 0:
            with open("system-message.txt", "r") as file:
                system_message = file.read()

            message_history = [
                {
                    "role": "system",
                    "content": system_message
                }
            ]
            self.update_message_history(message_history)
        else:
            for row in rows:

                if row[2] == "tool":
                    message = {
                        "tool_call_id": row[0],
                        "role": "tool",
                        "name": "search_web",
                        "content": row[3],
                    }
                elif bool(row[4]):
                    tool_calls = self.get_tools(row[0])

                    message = {
                        "role": row[2],
                        "content": row[3],
                        "tools_calls": tool_calls
                    }
                else:
                    message = {
                        "role": row[2],
                        "content": row[3]
                    }

                message_history.append(message)

        return message_history

    def get_tools(self, message_id: str) -> List[Dict[str, Any]]:
        rows = Database.get_tools(message_id)
        tool_calls = []

        for row in rows:
            tool_calls.append({
                "id": row[1],
                "type": row[2],
                "function": {
                    "name": row[3],
                    "arguments": row[4]
                }
            })

        return tool_calls

    def update_message_history(self, new_messages: List[Dict[str, Any]]):
        for message in new_messages:
            if message["role"] == "tool":
                Database.update_user_messages(self.uid, "tool", message["content"], str(message["tool_call_id"]))
            elif "tool_calls" in message.keys():
                row_id = str(uuid.uuid4())
                Database.update_user_messages(self.uid, str(message["role"]), message["content"], row_id, has_tool=True)
                for tool_call in message["tool_calls"]:
                    Database.update_tools(
                        row_id, tool_call["id"], tool_call["type"],
                        tool_call["function"]["name"], tool_call["function"]["arguments"]
                    )

    def clear_message_history(self):
        Database.clear_message_history(self.uid)

    async def create_completion(self, messages: [Dict[str, Any]]):
        completion = await self.client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=messages,
            tools=TOOLS
        )

        completion_message = completion.choices[0].message

        if tool_calls := completion_message.tool_calls:
            tool_calls = [{
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            } for tool_call in tool_calls]

            return ({
                "role": completion_message.role,
                "content": completion_message.content,
                "tool_calls": tool_calls
            }, completion)
        else:
            return ({
                "role": completion_message.role,
                "content": completion_message.content
            }, completion)

    async def send_message(self, prompt: str) -> AsyncGenerator[str, Any]:

        message_history = self.get_message_history()
        user_message = {
            "role": "user",
            "content": prompt
        }

        message, completion = await self.create_completion(messages=[*message_history, user_message])
        self.update_message_history([user_message, message])

        if tool_calls := message["tool_calls"]:
            yield "Searching the web..."

            tools = await handle_tools(tool_calls)
            message, completion = await self.create_completion(messages=
                                                               [*message_history, user_message, message, *tools])

            self.update_message_history([*tools, message])

        if completion.usage.total_tokens > 0.95 * MAX_TOTAL_TOKENS:
            Database.clear_message_history(self.uid)

        yield message["content"]
