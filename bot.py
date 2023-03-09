from flask import Flask, jsonify
from threading import Thread
import discord
from discord.ext import commands

app = Flask(__name__)
bot = commands.Bot(command_prefix="?", intents=discord.Intents.all())


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@app.route('/most_recent_message')
async def most_recent_message():
    
    channel = bot.get_channel(1073104398286340136)  # Replace with the ID of the channel you want to get the most recent message from
    async for message in channel.history(limit=1):
        return jsonify({'message': message.content})
    else:
        return jsonify({'message': 'No messages found'})

# thread function
def flask_thread(func):
    thread = Thread(target=func)
    print('Start Separate Thread From Bot')
    thread.start()


def run():
    app.run()

if __name__ == '__main__':
    flask_thread(func=run)
    bot.run('MTA3NzQ3NDM4Mzc3OTYwNjYwMA.GAejme.M9ozFBunjSXJOuFIjlSlh9trTuFSbtJflZn2nE')
