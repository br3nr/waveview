from discord.ext import commands
from quart import Quart, jsonify, websocket
import asyncio
import discord
import os
from music import Music
from discord import ClientException
from flask import abort
from utils import compare_images
from queue import Queue
import json
from quart_cors import cors
import requests

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
app = Quart(__name__)
cors(app)

@app.websocket('/ws')
async def ws():
    while True:
        try:
            await asyncio.sleep(0.1)  # Sleep for 0.1 seconds
            music_player = Music(bot).get_player()
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
            queue_list = list(music_player.queue)
            json_queue = []
            for i in range(len(queue_list)):
                track_id = queue_list[i].id
                track_title = queue_list[i].title
                try:
                    thumbnail_url = queue_list[i].thumbnail
                    if compare_images(thumbnail_url):
                        thumbnail_url = "/images/default.png"
                except AttributeError:
                    thumbnail_url = "/images/default.png"

                json_queue.append({
                    'id': i,
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

@app.route('/remove_track/<track>')
async def remove_track(track):
    try:
        Music(bot).dequeue_track_by_id(int(track))
        return "Ok"
    except IndexError:
        print("IndexError in remove_track. Calling track id: " + track)
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
