from discord.ext import commands
from quart import Quart, jsonify, websocket, request, make_response, redirect, session
import asyncio
import discord
import os
from music import Music
from discord import ClientException
from flask import abort
from utils import compare_images
import json
from quart_cors import cors
from zenora import APIClient 
import uuid 
from config import TOKEN, CLIENT_SECRET, REDIRECT_URI, OAUTH_URL, CLIENT_ID, SESSION_KEY

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
app = Quart(__name__)
app.secret_key = SESSION_KEY
cors(app)

api_client = APIClient(TOKEN, client_secret=CLIENT_SECRET)


@app.route("/auth/redirect")
async def callback():
    code = request.args.get("code")
    access_token = api_client.oauth.get_access_token(code, REDIRECT_URI).access_token
    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()
    response = await make_response(redirect("http://localhost:3000/posts/music-dashboard"))
    
    user = {
        "id": str(current_user.id),
        "discriminator": str(current_user.discriminator),
        "name": str(current_user.username),
        "avatar_url": str(current_user.avatar_url),
        "username": str(current_user.username),
        "access_token": str(access_token) # may need to remove for security
    }

    session_id = str(uuid.uuid4())
    
    while session_id in session: # make sure the uuid is unique
        session_id = str(uuid.uuid4())
    
    session[session_id] = user
    response.set_cookie("session_id", session_id)
    return response

@app.route("/auth/login/<session_id>")
async def login(session_id):
    session_keys = session.keys()
    print(session_keys)
    print(session_id)
    if session_id in session.keys():
        return jsonify(session[session_id])
    else:
        return abort(401)

@app.websocket('/ws')
async def ws():
    while True:
        try:
            await asyncio.sleep(0.1)  # Sleep for 0.1 seconds
            music_cls = Music(bot)
            music_player = music_cls.get_player()
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

            # Get the queue information
            queue_list = music_cls.get_queue()
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

            track_info['queue'] = json_queue
        except AttributeError as e:
            track_info = {
                'title': "No track playing",
                'thumbnail': "/images/default.png",
                'queue': []
            }
            print(e)

        # Send the JSON data through the websocket
        await websocket.send(json.dumps(track_info))


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


@app.route('/get_servers')
async def get_servers():
    active_servers = bot.guilds
    guild_list = []
    for guild in active_servers:
        print(guild.id)
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
        vc_list.append({"vc_name": str(vc.name),
                        "vc_id": str(vc.id)})
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


@app.route('/remove_track/<track_id>')
async def remove_track(track_id):
    try:
        await Music(bot).dequeue_track_by_id(track_id)
        return "Ok"
    except IndexError:
        print("IndexError in remove_track. Calling track id: " + track_id)
        abort(500)


@app.route('/play_song/<query>')
async def play_song(query):
    try:
        await Music(bot).play_song_by_query(query)
        return "Ok"
    except IndexError:
        print("IndexError in remove_track. Calling track id: " + track_id)
        abort(500)


@app.route('/song')
async def song():
    # Return most recent message
    song = Music(bot).get_current_song()

    return jsonify({'message': str(song.title)})


@app.route('/playing')
async def playing():
    try:
        music_player = Music(bot).get_player()
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


@app.route('/queue')
async def queue():

    music_player = Music(bot).get_player()
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


@app.route('/pause')
async def pause():
    await Music(bot).pause_track()
    return "OK"


@app.route('/restart')
async def restart():
    await Music(bot).restart()
    return "OK"


@app.route('/skip')
async def skip():
    await Music(bot).skip_track()
    return "OK"


@app.route('/resume')
async def resume():
    await Music(bot).resume_track()
    return "OK"


@app.route('/thumbnail')
async def thumbnail():
    try:
        thumbnail = await Music(bot).get_thumbnail()
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
    asyncio.run(main())
