import os
import discord
from discord.ext import commands
from src.music.music_control import Music
from src.music.music_commands import MusicCommands
import asyncio
from fastapi import FastAPI
import asyncio
from src.routers.auth_router import AuthRouter
from src.routers.player_router import PlayerRouter
from src.routers.player_ws import PlayerWebsocket
from config import (
    TOKEN,
    CLIENT_SECRET
)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
player = Music(bot)
app = FastAPI(debug=True)

auth_router = AuthRouter(TOKEN, CLIENT_SECRET)
music_router = PlayerRouter(bot, player)
player_ws = PlayerWebsocket(bot, player)

app.include_router(auth_router, tags=["auth"])
app.include_router(music_router, tags=["music"])
app.include_router(player_ws, tags=["player_ws"])


@bot.event
async def on_connect():
    print("Connected to Discord")
    await bot.add_cog(player)
    player.initialise_player()
    await bot.add_cog(MusicCommands(bot))
    print("Music cogs added to bot")


async def run():
    try:
        await bot.start(os.environ["DEV_CLIENT_ID"])
    except KeyboardInterrupt:
        await bot.logout()


asyncio.create_task(run())
