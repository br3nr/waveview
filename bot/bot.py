from threading import Thread
import discord
from discord.ext import commands
from quart import Quart, jsonify
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from wavelink.ext import spotify
import re
import os
from music import Music
from discord import ClientException


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
app = Quart(__name__)
m = None

@bot.event
async def on_ready():
    try:
        print('Logged in as {0.user}'.format(bot))
        global m 
        m = Music(bot)
        await bot.add_cog(m)
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
    m.get_current_song()  
    
    return jsonify({'message': 'hi'})


@bot.command()
async def hello(ctx):
    await ctx.send('Hello, World!')


async def start_app():
    await app.run_task(host='0.0.0.0', port=5010)


async def start_bot():
    await bot.start('')


async def main():
    await asyncio.gather(start_app(), start_bot())

if __name__ == '__main__':
    asyncio.run(main())
