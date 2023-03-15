from discord.ext import commands
from quart import Quart, jsonify
import asyncio
import discord
import os
from music import Music
from discord import ClientException

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
app = Quart(__name__)

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

@app.route('/song')
async def song():
    # Return most recent message
    song = Music(bot).get_current_song()  
    
    return jsonify({'message': str(song.title)})

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
    thumbnail = await Music(bot).get_thumbnail()
    return {'thumbnailUrl': thumbnail}

@bot.command()
async def hello(ctx):
    await ctx.send('Hello, World!')


async def start_app():
    await app.run_task(host='0.0.0.0', port=5010)


async def start_bot():
    await bot.start(os.environ["DEV_CLIENT_ID"])


async def main():
    await asyncio.gather(start_app(), start_bot())

if __name__ == '__main__':
    asyncio.run(main())
