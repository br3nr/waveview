import asyncio
import discord
import os
from src.session.session_manager import SessionManager
from fastapi import FastAPI, HTTPException
from discord.ext import commands
from src.music.music_control import Music
from src.routers.auth_router import AuthRouter
from src.routers.player_router import PlayerRouter
from src.routers.player_ws import PlayerWebsocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# NOTE: Replace the default None in os.environ.get with the
# corresponding value, otherwise set as environment variable

# REQUIRED: Env variables for your bot token, client_id, and client_secret
# These can be found in the developer portal under Bot and OAuth2 -> General
BOT_TOKEN = os.environ.get(
    "BOT_TOKEN",
    "",
)
BOT_CLIENT_ID = os.environ.get("BOT_CLIENT_ID", "")
BOT_CLIENT_SECRET = os.environ.get(
    "BOT_CLIENT_SECRET", ""
)
# These can be found in the developer portal under Bot and OAuth2 -> General
# OPTIONAL: Leave as blank if you don't want to use Spotify
SPOTIFY_CLIENT_SECRET = os.environ.get(
    "SPOTIFY_CLIENT_SECRET", ""
)
SPOTIFY_CLIENT_ID = os.environ.get(
    "SPOTIFY_CLIENT_ID", ""
)

# REQUIRED: Change these if you plan on hosting thisoutside of localhost
LAVALINK_URI = os.environ.get("LAVALINK_URI", default="http://0.0.0.0:2333")
REDIRECT_LOC = os.environ.get(
    "REDIRECT_LOC", default="http://localhost:3000/server-select"
)
REDIRECT_URI = os.environ.get(
    "REDIRECT_URI", default="http://localhost:5090/auth/redirect"
)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
player = Music(bot, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, LAVALINK_URI)
app = FastAPI(debug=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

auth_router = AuthRouter(BOT_TOKEN, BOT_CLIENT_SECRET, REDIRECT_URI, REDIRECT_LOC)
music_router = PlayerRouter(bot, player)
player_ws = PlayerWebsocket(bot, player)

app.include_router(auth_router, tags=["auth"])
app.include_router(music_router, tags=["music"])
app.include_router(player_ws, tags=["player_ws"])


@app.middleware("http")
async def authenticate_request(request, call_next):
    if request.url.path.startswith("/auth"):
        response = await call_next(request)
        return response

    token = request.cookies.get("session_id")
    session_manager = SessionManager.get_instance()

    if session_manager.is_authenticated(token):
        response = await call_next(request)
        return response
    else:
        raise HTTPException(
            status_code=401, detail="Not authorised to perform this action."
        )


@bot.event
async def on_connect():
    print("Connected to Discord")
    await bot.add_cog(player)
    player.initialise_player()
    print("Cogs added to bot")


async def run():
    try:
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        await bot.logout()


asyncio.create_task(run())
