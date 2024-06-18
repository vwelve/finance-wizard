from typing import List

from openai import AsyncOpenAI
from utils import TOOLS, count_tokens

MESSAGE_HISTORY = {}
MAX_DISCORD_MESSAGE_LENGTH = 2000


def clear_message_history(uid):
    MESSAGE_HISTORY[uid] = []


async def send_openai_messages(message_history):
    client = AsyncOpenAI()

    completion = await client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        messages=message_history,
        tools=TOOLS
    )

    message = completion.choices[0].message
    print(message)

    if count_tokens(message_history) >= 30000:
        message_history.pop(1)
        return

    if message.content and len(message.content) > MAX_DISCORD_MESSAGE_LENGTH:
        message_history.append(message)
        message_history.append({
            "role": "user",
            "content": f"Make this message more concise it is too long, don't let it exceed {MAX_DISCORD_MESSAGE_LENGTH} characters."
        })
        return await send_openai_messages(message_history)
    return message


def get_message_history(uid):
    user_history = MESSAGE_HISTORY.get(uid)

    if user_history is None:
        with open("system-message.txt", "r") as file:
            system_message = file.read()

        user_history = [{
            "role": "system",
            "content": system_message
        }]

        MESSAGE_HISTORY[uid] = user_history

    return user_history


def set_message_history(uid, history):
    MESSAGE_HISTORY[uid] = history
