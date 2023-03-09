from quart import Quart, render_template, redirect, url_for
from quart_discord import DiscordOAuth2Session
import os

os.environ[
    "OAUTHLIB_INSECURE_TRANSPORT"
] = "1"  # this is required because OAuth 2 utilizes https.

app = Quart(__name__)

app.config["SECRET_KEY"] = "test123"

app.config["DISCORD_CLIENT_ID"] = 1077474383779606600  # Discord client ID.
app.config[
    "DISCORD_CLIENT_SECRET"
] = "RVDExOtMJIoaVBZ4STjbBlAgFF5QLT9Y"  # Discord client secret.
app.config[
    "DISCORD_REDIRECT_URI"
] = "http://127.0.0.1:5000/callback"  # URL to your callback endpoint.

discord = DiscordOAuth2Session(app) #handle session for authentication

@app.route("/")
async def home():
    return await render_template("home.html", authorized=await discord.authorized)

@app.route("/login")
async def login():
    return await discord.create_session() # handles session creation for authentication

@app.route("/callback")
async def callback():
    try:
        await discord.callback()
    except Exception:
        pass

    return redirect(url_for("dashboard")) #dashboard function will be  created later in the a
