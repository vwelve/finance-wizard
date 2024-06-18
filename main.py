import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from openai import OpenAIError
from exceptions import ToolFunctionError
from gpt import send_openai_messages, get_message_history, set_message_history
from utils import handle_tools
import discord
import os
import logging

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR)

load_dotenv()
ALLOWED_CHANNEL = int(os.getenv("ALLOWED_CHANNEL"))
DEV_MODE = os.getenv("CODE_ENVIRONMENT") == "dev"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command(name='gpt', help='Responds with AI-generated text based on your prompt')
async def _gpt(ctx, *, prompt: str):
    if not DEV_MODE and ctx.channel.id != ALLOWED_CHANNEL:
        await ctx.send(f"I can only reply in <#{ALLOWED_CHANNEL}>")
    else:
        uid = ctx.message.author.id
        message_history = get_message_history(uid)
        message = [
            {
                "role": "user",
                "content": prompt
            },
            *[
                {
                    "type": "image_url",
                    "image_url":
                        {
                            "url": attachment.url
                        }
                }
                for attachment in ctx.message.attachments]
        ]

        message_history = [*message_history, *message]
        discord_message = await ctx.send("Give me a sec...")

        try:
            message = await send_openai_messages(message_history)
            message_history.append(message)
            print(f"Message: {message}")

            if tool_calls := message.tool_calls:
                await discord_message.edit(content="Searching the web...")
                print(f"Tried to run tools: {tool_calls}")
                tool_response = await handle_tools(tool_calls)
                message_history = [*message_history, *tool_response]
                print(f"Tools ran with: {message}")
                message = await send_openai_messages(message_history)
                message_history.append(message)

            set_message_history(uid, message_history)
            await discord_message.edit(content=message.content)
        except OpenAIError as e:
            set_message_history(uid, [])
            await discord_message.edit(
                content="There was an issue reaching the server. Report this issue and try again later.")
            logging.error("An OpenAIError occurred", exc_info=True)
        except ToolFunctionError:
            await discord_message.edit(
                content="There was an issue searching the web. Report this issue and try again later."
            )
            logging.error("A ToolFunctionError occurred", exc_info=True)
        except Exception as e:
            await discord_message.edit(
                content=f"There was an unknown error. Report this issue and try again later."
            )
            logging.error("A BaseError occurred", exc_info=True)


@bot.command(name='clear', help='Responds with AI-generated text based on your prompt')
async def clear(ctx):
    uid = ctx.message.author.id
    set_message_history(uid, None)

    await ctx.send("Your message history has been cleared")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.start(os.getenv("DISCORD_TOKEN")))
