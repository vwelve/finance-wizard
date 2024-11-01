import asyncio

from openai import AuthenticationError, RateLimitError

from discord import NotFound

import discord
from dotenv import load_dotenv
from discord.ext import commands
import openai

import os
import logging

from db.database import Database
from gpt.finance_wizard import FinanceWizard
from util.exceptions import ToolFunctionError


# Configure logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

load_dotenv()
ALLOWED_CHANNEL = int(os.getenv("ALLOWED_CHANNEL"))
DEV_MODE = os.getenv("CODE_ENVIRONMENT") == "dev"
COMMAND_PREFIX = "$"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)


@bot.event
async def on_ready():
    logging.info(f'We have logged in as {bot.user}')


@bot.command(name="start")
async def start(ctx):
    if not DEV_MODE and ctx.channel.id != ALLOWED_CHANNEL:
        await ctx.send(f"I can only reply in <#{ALLOWED_CHANNEL}>")
    else:
        uid = ctx.message.author.id
        channel_id = Database.get_user_channel(uid)
        channel_id = int(channel_id) if bool(channel_id) else 0
        channel = None
        user = ctx.message.author
        guild = ctx.guild

        try:
            channel = await ctx.guild.fetch_channel(channel_id)
        except NotFound:
            overwrites = {
                ctx.message.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }

            channel = await guild.create_text_channel(f"{user.name}-finance_wizard", overwrites=overwrites, position=0)
            Database.update_user_channel(uid, channel.id)
        finally:
            token = Database.get_user_token(uid)

            if token:
                await channel.send(f"""<@{uid}>
Here is your private channel to chat.

Example:
{COMMAND_PREFIX}gpt *prompt*""")
            else:
                await channel.send(f"""
<@{uid}>
Set your OpenAI token before trying to chat.
                
Example:
{COMMAND_PREFIX}token *token*
{COMMAND_PREFIX}gpt *prompt*""")


@bot.command(name="token")
async def _token(ctx, *, token: str):
    uid = ctx.message.author.id
    channel_id = Database.get_user_channel(uid)
    channel_id = int(channel_id) if bool(channel_id) else 0

    if channel_id == ctx.message.channel.id:
        Database.set_user_token(ctx.message.author.id, token)
        await ctx.send("Successfully set your token.")
    else:
        await ctx.send(f"You can only run this command in your channel. If you can't find your channel do "
                       f"{COMMAND_PREFIX}start in <#{ALLOWED_CHANNEL}>")
        

@bot.command(name='gpt', help='Responds with AI-generated text based on your prompt')
async def _gpt(ctx, *, prompt: str):
    uid = ctx.message.author.id
    channel_id = Database.get_user_channel(uid)
    channel_id = int(channel_id) if bool(channel_id) else 0
    token = Database.get_user_token(uid)
    if ctx.channel.id != channel_id:
        await ctx.send(f"You can only run this command in your channel. If you can't find your channel do "
                       f"{COMMAND_PREFIX}start in <#{ALLOWED_CHANNEL}>")
    elif not DEV_MODE and not token:
        await ctx.send(f"You have no token assigned yet. Run {COMMAND_PREFIX}token *token*")
    else:
        fw = FinanceWizard(uid, token)
        discord_message = await ctx.send("Give me a sec...")

        try:
            async for message in fw.send_message(prompt):
                await discord_message.edit(content=message)
        except AuthenticationError:
            await discord_message.edit(content="There was an authentication issue. Are you sure you properly set your "
                                               "OpenAI token?")
            logging.error("An OpenAIError occurred", exc_info=True)
        except ToolFunctionError:
            await discord_message.edit(content="There was an issue searching the web. Report this issue and try again "
                                               "later.")
            logging.error("A ToolFunctionError occurred", exc_info=True)
        except RateLimitError:
            await discord_message.edit(content="There was a rate limit error. Try again later. If the issue persists"
                                               "then check your account for insufficient funds.")
        except Exception as e:
            await discord_message.edit(content="There was an unknown error. Report this to the admins.")
            logging.error("A BaseError occurred", exc_info=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.start(os.getenv("DISCORD_TOKEN")))
