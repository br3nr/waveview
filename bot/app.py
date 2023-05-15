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

# NOTE: Replace the default None in os.environ.get with the 
# corresponding value, otherwise set as environment variable

# REQUIRED: Env variables for your bot token, client_id, and client_secret
# These can be found in the developer portal under Bot and OAuth2 -> General 
BOT_TOKEN = os.environ.get(["BOT_TOKEN"], None)
BOT_CLIENT_ID = os.environ.get("BOT_CLIENT_ID", None)
BOT_CLIENT_SECRET = os.environ.get("BOT_CLIENT_SECRET", None)

# OPTIONAL: Leave as blank if you don't want to use Spotify
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", None)
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", None)

# REQUIRED: Change these if you plan on hosting thisoutside of localhost
LAVALINK_URI = os.environ.get("LAVALINK_URI", default="http://0.0.0.0:2333")
REDIRECT_LOC = os.environ.get("REDIRECT_LOC", default="http://localhost:3000/posts/server-select")
REDIRECT_URI = os.environ.get("REDIRECT_URI", default="http://localhost:5090/auth/redirect")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
player = Music(bot, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, LAVALINK_URI)
app = FastAPI(debug=True)

auth_router = AuthRouter(BOT_TOKEN, BOT_CLIENT_SECRET, REDIRECT_URI, REDIRECT_LOC)
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
