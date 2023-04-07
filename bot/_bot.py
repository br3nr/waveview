from discord.ext import commands
from quart import Quart, jsonify, websocket, request, make_response, redirect, session
import asyncio
import discord
import os
import argparse
from music import Music
from flask import abort
import json
from quart_cors import cors
import uuid
import sys 

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
app = Quart(__name__)
app.secret_key = SESSION_KEY
cors(app)
is_vps = False

# 212e8574-4605-468a-8d0b-746706f321fe
# bad== Xl9pX6kZdJptNckoh4pxKOjOpezEG7
# good= D8cfW5Ai1iaX163N6u3vAOKrJ7YgcT


@app.route("/auth/redirect")
async def callback():
    code = request.args.get("code")
    # http://45.32.191.6:5090/auth/redirect
    
    access_token = api_client.oauth.get_access_token(
    code, REDIRECT_URI).access_token
    
    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    response = await make_response(redirect(REDIRECT_LOC))
    
    user = {
        "id": str(current_user.id),
        "discriminator": str(current_user.discriminator),
        "name": str(current_user.username),
        "avatar_url": str(current_user.avatar_url),
        "username": str(current_user.username),
        "access_token": str(access_token)  # may need to remove for security
    }

    session_id = str(uuid.uuid4())

    while session_id in session:  # make sure the uuid is unique
        session_id = str(uuid.uuid4())

    session[session_id] = user
    response.set_cookie("session_id", session_id)
    return response


@app.route("/auth/login/<session_id>")
async def login(session_id):
    if session_id in session.keys():
        return jsonify(session[session_id])
    else:
        return abort(401)




























@bot.command()
async def hello(ctx):
    await ctx.send('Hello, World!')


async def start_app():
    await app.run_task(host='0.0.0.0', port=5090)


async def start_bot():
    await bot.start(os.environ["DEV_CLIENT_ID"])


async def main():
    await asyncio.gather(start_app(), start_bot())

if __name__ == '__main__':
    # check if the --vps flag is set
    if len(sys.argv) > 1 and sys.argv[1] == "--vps":
        is_vps = True

        

    asyncio.run(main())
