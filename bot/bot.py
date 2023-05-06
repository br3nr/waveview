import os
import discord
from discord.ext import commands
from src.music.music_control import Music
from src.music.music_commands import MusicCommands

import asyncio
from src.api.api import BotAPI
from config import TOKEN, CLIENT_SECRET, REDIRECT_URI, SESSION_KEY, REDIRECT_LOC, VPS_REDIRECT_URI

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
app = BotAPI(bot, TOKEN, CLIENT_SECRET).app


@bot.event
async def on_connect():
    print('Connected to Discord')
    await bot.add_cog(Music(bot))
    await bot.add_cog(MusicCommands(bot))
    print('Music cogs added to bot')

async def run():
    try:
        await bot.start(os.environ["DEV_CLIENT_ID"])

    except KeyboardInterrupt:
        await bot.logout()

asyncio.create_task(run())