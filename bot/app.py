import asyncio
import discord
from fastapi import FastAPI
import os
from discord.ext import commands
from src.music.music_control import Music
from src.music.music_commands import MusicCommands
from src.routers.auth_router import AuthRouter
from src.routers.player_router import PlayerRouter
from src.routers.player_ws import PlayerWebsocket
from config import (
    BOT_TOKEN,
    BOT_OAUTH_SECRET,
    REDIRECT_LOC,
    REDIRECT_URI,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET
)

try: # Helps w local testing
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    BOT_CLIENT_ID = os.environ["BOT_CLIENT_ID"]
    BOT_OAUTH_SECRET = os.environ["BOT_OAUTH_SECRET"]
    SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
    SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
except KeyError:
    pass

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
player = Music(bot, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
app = FastAPI(debug=True)

auth_router = AuthRouter(BOT_TOKEN, BOT_OAUTH_SECRET, REDIRECT_URI, REDIRECT_LOC)
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
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.logout()


asyncio.create_task(run())
