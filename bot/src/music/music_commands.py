from discord.ext import commands
from log import log_command
from .custom_player import CustomPlayer
from .music_utils import check_string
from .music_players import *

class MusicCommands(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command()
    @log_command
    async def join(self, ctx):
        vc = ctx.voice_client
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send("How can I join if you are nowhere to be found?")
        if vc:
            await vc.disconnect()
        await channel.connect(cls=CustomPlayer())

    @commands.command()
    @log_command
    async def leave(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
        else:
            await ctx.send("how can i disconnect when i am not connect?")

    @commands.command()
    @log_command
    async def play(
        self,
        ctx: commands.Context,
        *,
        search: str = commands.parameter(
            description="Plays a song from url or query. Accepted urls are: spotify [track,album,playlist], youtube."
        ),
    ):

        url_type = check_string(search)
        action = self.url_type_mapping.get(url_type, None)
        vc = ctx.voice_client
        if not vc:
            custom_player = CustomPlayer()
            vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)
        if action:
            await action(self, ctx, search, vc)
        else:
            # handle text input
            await ctx.send("Idk that link is suss. Try again.")

    @commands.command()
    @log_command
    async def pause(self, ctx):
        """Skips the current song."""
        vc = ctx.voice_client
        if vc:
            if vc.is_playing() and not vc.is_paused():
                await vc.pause()
            else:
                await ctx.send("Nothing is playing.")
        else:
            await ctx.send("The bot is not connected to a voice channel")

    @commands.command()
    @log_command
    async def resume(self, ctx):
        """Resumes the current song."""
        vc = ctx.voice_client
        if vc:
            if vc.is_paused():
                await vc.resume()
            else:
                await ctx.send("Nothing is paused.")
        else:
            await ctx.send("The bot is not connected to a voice channel")

    @commands.command()
    @log_command
    async def skip(self, ctx):
        """Skip the current song."""
        vc = ctx.voice_client
        if vc:
            if not vc.is_playing():
                return await ctx.send("Nothing is playing.")
            if vc.queue.is_empty:
                return await vc.stop()

            await vc.seek(vc.current.length * 1000)
            if vc.is_paused():
                await vc.resume()
        else:
            await ctx.send("The bot is not connected to a voice channel.")