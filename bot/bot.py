from discord.ext import commands
from quart import Quart, jsonify, websocket, request, make_response, redirect, session
import asyncio
import discord
import os
import argparse
from music import Music
from discord import ClientException
from flask import abort
from utils import compare_images
import json
from quart_cors import cors
from zenora import APIClient
import uuid
from config import TOKEN, CLIENT_SECRET, REDIRECT_URI, SESSION_KEY, REDIRECT_LOC, VPS_REDIRECT_URI
import sys 

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
app = Quart(__name__)
app.secret_key = SESSION_KEY
cors(app)
is_vps = False

api_client = APIClient(TOKEN, client_secret=CLIENT_SECRET)
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


@app.websocket('/ws')
async def ws():
    music_cls = Music(bot)
    while True:
        try:
            await asyncio.sleep(0.1)  # Sleep for 0.1 seconds
            guilds = music_cls.get_guilds()
            guild_tracks = {}
            for guild in guilds:
                music_player = music_cls.get_player(guild.id)
                if music_player is not None:  # Check if music_player is not None
                    try:
                        # Get info about the current track
                        thumbnail_url = music_player.source.thumbnail
                        if compare_images(thumbnail_url):
                            thumbnail_url = "/images/default.png"
                        track_title = music_player.source.title
                    except AttributeError as e:
                        thumbnail_url = "/images/default.png"
                        track_title = "No track playing"
                
                    track_info = {
                        'title': track_title,
                        'thumbnail': thumbnail_url
                    }

                    guild_tracks[str(guild.id)] = track_info
                    queue_list = music_cls.get_queue(str(guild.id))
                    json_queue = []

                    for i in range(len(queue_list)):
                        track_uuid = queue_list[i].uuid
                        track_title = queue_list[i].track.title
                        try:
                            thumbnail_url = queue_list[i].track.thumbnail
                            if compare_images(thumbnail_url):
                                thumbnail_url = "/images/default.png"
                        except AttributeError:
                            thumbnail_url = "/images/default.png"

                        json_queue.append({
                            'id': i,
                            'uuid': track_uuid,
                            'title': track_title,
                            'thumbnail': thumbnail_url
                        })
                
                    guild_tracks[str(guild.id)]['queue'] = json_queue

                else:
                    guild_tracks[str(guild.id)] = {
                        'title': "No track playing",
                        'thumbnail': "/images/default.png",
                        'queue': []
                    }

            # Send the JSON data through the websocket
            await websocket.send(json.dumps(guild_tracks))
        except AttributeError as e:
            print(e)

@bot.event
async def on_ready():
    try:
        print('Logged in as {0.user}'.format(bot))
        music = Music(bot)
        await bot.add_cog(music)
        synced = await bot.tree.sync()
    except ClientException:
        print("Failed to sync")


@bot.event
async def on_connect():
    print('Connected to Discord')
    await bot.add_cog(Music(bot))
    print('Music cog added to bot')


@app.route('/get_servers/<user_id>')
async def get_servers(user_id):
    active_servers = bot.guilds
    guild_list = []

    for guild in active_servers:
        if guild.get_member(int(user_id)):
            guild_list.append({"id": str(guild.id),
                               "name": str(guild.name),
                               "icon": str(guild.icon.url)})
    return jsonify(guild_list)


@app.route('/get_vc/<guild_id>')
async def get_vc(guild_id):
    print(guild_id)
    guild = bot.get_guild(int(guild_id))
    vc_list = []
    for vc in guild.voice_channels:
        is_connected = False
        if guild.voice_client and guild.voice_client.channel == vc:
            is_connected = True
        vc_list.append({
            "vc_name": str(vc.name),
            "vc_id": str(vc.id),
            "is_connected": is_connected
        })
    print(vc_list)
    return jsonify(vc_list)


@app.route('/join_vc/<guild_id>/<vc_id>')
async def join_vc(guild_id, vc_id):
    print("Joining vc: " + vc_id + " in guild: " + guild_id + "")
    await Music(bot).join_vc(int(guild_id), int(vc_id))
    return "Success", 200


@app.route('/ping')
async def ping():
    return jsonify({'message': 'pong'})


@app.route('/message')
async def message():
    # Return most recent message
    channel = bot.get_channel(1073104398286340136)

    async for message in channel.history(limit=1):
        return jsonify({'message': message.content})
    else:
        return jsonify({'message': 'No messages found'})


@app.route('/remove_track/<guild_id>/<track_id>')
async def remove_track(guild_id, track_id):
    try:
        await Music(bot).dequeue_track_by_id(guild_id, track_id)
        return "Ok"
    except IndexError:
        print("IndexError in remove_track. Calling track id: " + track_id)
        abort(500)


@app.route('/play_song/<guild_id>', methods=["POST"])
async def play_song(guild_id):
    try:
        data = await request.get_json()
        url = data.get("url")
        print("Playing song: " + url + " in guild: " + guild_id + "")
        await Music(bot).play_song_by_query(guild_id, url)
        return "Ok"
    except IndexError:
        print("IndexError in remove_track. Calling track id: " + url)
        abort(500)


@app.route('/song')
async def song():
    # Return most recent message
    song = Music(bot).get_current_song()

    return jsonify({'message': str(song.title)})


@app.route('/playing/<guild_id>')
async def playing(guild_id):
    try:
        music_player = Music(bot).get_player(guild_id)
        thumbnail_url = music_player.source.thumbnail

        # Check if thumbnail is the default image
        if compare_images(thumbnail_url):
            thumbnail_url = "/images/default.png"

        return jsonify({
            'title': music_player.source.title,
            'thumbnail': thumbnail_url
        })

    except AttributeError:
        abort(500)


@app.route('/queue/<guild_id>')
async def queue(guild_id):

    music_player = Music(bot).get_player(guild_id)
    queue_list = list(music_player.queue)
    json_queue = []

    # loop through queue
    for i in range(len(queue_list)):
        thumbnail_url = queue_list[i].thumbnail
        track_title = queue_list[i].title
        # add to dict
        if compare_images(thumbnail_url):
            thumbnail_url = "/images/default.png"
        json_queue.append({
            'title': track_title,
            'thumbnail': thumbnail_url
        })

    return jsonify({"queue": json.dumps(json_queue)})


@app.route('/pause/<guild_id>')
async def pause(guild_id):
    await Music(bot).pause_track(guild_id)
    return "OK"


@app.route('/skip/<guild_id>')
async def skip(guild_id):
    await Music(bot).skip_track(guild_id)
    return "OK"


@app.route('/resume/<guild_id>')
async def resume(guild_id):
    await Music(bot).resume_track(guild_id)
    return "OK"


@app.route('/thumbnail/<guild_id>')
async def thumbnail(guild_id):
    try:
        thumbnail = await Music(bot).get_thumbnail(guild_id)
        return {'thumbnailUrl': thumbnail}
    except AttributeError:
        abort(500)


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
