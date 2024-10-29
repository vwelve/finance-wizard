from openai import AsyncOpenAI

from typing import List, Union, Generator

from gpt.message import GPTMessage, RoleType
from gpt.tools import handle_tools, TOOLS
from db.database import Database

MAX_TOTAL_TOKENS = 32768


class FinanceWizard:
    def __init__(self, uid: str, token: str):
        self.uid = uid
        self.token = token

    def get_message_history(self) -> List[Union[GPTMessage, dict]]:
        rows = Database.get_user_messages(self.uid)
        message_history = []

        if len(rows) == 0:
            with open("system-message.txt", "r") as file:
                system_message = file.read()

            message_history = [
                GPTMessage(role=RoleType.SYSTEM, content=system_message)
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
                else:
                    message = GPTMessage(role=row[2], content=row[3])

                message_history.append(message)

        return message_history

    def update_message_history(self, new_messages: List[Union[GPTMessage, dict]]):
        for message in new_messages:
            if message.role == "tool":
                Database.update_message_history(self.uid, "tool", message.content, message.tool_call_id)
            else:
                Database.update_message_history(self.uid, message.role, message.content)

    def clear_message_history(self):
        Database.clear_message_history(self.uid)

    async def send_message(self, prompt: str) -> Generator[str, None, None]:
        client = AsyncOpenAI()
        message_history = self.get_message_history()
        new_message = GPTMessage(role=RoleType.USER, content=prompt)

        completion = await client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=[*message_history, new_message.dict()],
            tools=TOOLS,
            api_key=self.token
        )
        message = completion.choices[0].message
        self.update_message_history([new_message, message])

        if tool_calls := message.tool_calls:
            yield "Searching the web..."
            tools = handle_tools(tool_calls)

            completion = await client.chat.completions.create(
                model="gpt-4o-2024-05-13",
                messages=[*message_history, *tools],
                tools=TOOLS,
                api_key=self.token
            )
            message = completion.choices[0].message

            self.update_message_history([*tools, message])

        if completion.usage.total_tokens > 0.95 * MAX_TOTAL_TOKENS:
            Database.clear_message_history(self.uid)

        yield message.content
