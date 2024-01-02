from discord.ext import commands
import wavelink
#from wavelink.ext import spotify
import os
import uuid
from src.logger.log import log_command
from discord import ClientException
import asyncio
from .custom_player import CustomPlayer
from .music_utils import check_string
from typing import cast 
import discord
from discord import Guild

class MiddleQueue:
    def __init__(self, track, thumbnail_uri=None):
        self.uuid = str(uuid.uuid4())
        self.track = track
        self.thumbnail_uri = thumbnail_uri

class Music(commands.Cog):

    def __init__(self, bot: commands.Bot, spotify_id, spotify_secret, lavalink_uri):
        self.bot = bot
        self.song_queue = {}
        self.cid = spotify_id
        self.csecret = spotify_secret
        self.middlequeues = {}
        self.lavalink_uri = lavalink_uri
        # for each guild, create a middlequeue
        for guild in self.bot.guilds:
            self.middlequeues[str(guild.id)] = []

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # Handle edge cases...
            return
        guild_id = player.guild.id
        cur_queue = self.middlequeues[str(guild_id)].pop(0)
        self.middlequeues[guild_id] = cur_queue
    
    async def setup_hook(self) -> None:
        nodes = [wavelink.Node(uri=self.lavalink_uri, password="1234")]
        # cache_capacity is EXPERIMENTAL. Turn it off by passing None
        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)
    
    def initialise_player(self):
        self.bot.loop.create_task(self.setup_hook())

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f"Node: <{node.identifier}> is ready!")

    def get_queue(self, guild_id):
        if guild_id in self.middlequeues:
            return self.middlequeues[guild_id]
        else:
            return []

    async def dequeue_track_by_id(self, guild_id, track_id):
        guild = self.bot.get_guild(int(guild_id))

        cur_queue = self.middlequeues[guild_id]
        # delete from middlequeue where uuid == track_id
        for i in range(len(cur_queue)):
            if cur_queue[i].uuid == track_id:
                del cur_queue[i]
                break

        wavelinkQueue = wavelink.Queue()
        # loop through queue_list and add to wavelinkQueue
        for i in range(len(cur_queue)):
            wavelinkQueue.put(cur_queue[i].track)

        guild.voice_client.queue = wavelinkQueue
        self.middlequeues[guild_id] = cur_queue

    async def reorder_queue(self, guild_id, uuid, new_position):
        guild = self.bot.get_guild(int(guild_id))
        cur_queue = self.middlequeues[guild_id]

        for i in range(len(cur_queue)):
            if cur_queue[i].uuid == uuid:
                track = cur_queue[i]
                del cur_queue[i]
                cur_queue.insert(new_position, track)
                break

        wavelinkQueue = wavelink.Queue()
        for i in range(len(cur_queue)):
            wavelinkQueue.put(cur_queue[i].track)

        guild.voice_client.queue = wavelinkQueue

    async def delete_queue_by_guild(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            vc.queue.reset()
            self.middlequeues[guild_id] = []

    def get_player(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        return vc

    async def pause_track(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            if vc.playing and not vc.paused:
                await vc.pause(True)

    async def resume_track(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            if vc.paused:
                await vc.pause(False)

    async def skip_track(self, guild_id):
        guild: Guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        player: wavelink.Player = cast(wavelink.Player, vc)
        if player:
            if len(player.queue) == 0:
                return await player.stop()
            res = await player.skip(force=True)
            print(res)

    async def restart(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        queue = vc.queue
        await vc.play(vc.current)
        vc.queue = queue

    async def seek_track(self, guild_id, seek_time):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        await vc.seek(seek_time)

    async def get_thumbnail(self, guild_id):
        print("ping")
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        return vc.current.artwork

    def get_guilds(self):
        return self.bot.guilds

    async def play_song_by_query(self, guild_id, query):
        guild: Guild | None = self.bot.get_guild(int(guild_id))

        vc = guild.voice_client
        player = cast(wavelink.Player, vc)  # type: ignore 

        player.autoplay = wavelink.AutoPlayMode.enabled 
        tracks: wavelink.Search = await wavelink.Playable.search(query)
        cur_queue = self.middlequeues.get(guild_id, [])

        if isinstance(tracks, wavelink.Playlist):
            for track in tracks:
                if player.playing:
                    cur_queue.append(MiddleQueue(track))
                    await player.queue.put_wait(track)
                else:
                    await player.play(track)
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            if player.playing:
                cur_queue.append(MiddleQueue(track))

        if not player.playing:
            await player.play(player.queue.get(), volume=30)
    
        self.middlequeues[guild_id] = cur_queue
    
    async def join_vc(self, guild_id, vc_id):
        # TODO: Work out why I used a while loop here
        # what was I trying to prevent?
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        while not vc or vc.channel.id != vc_id:
            if vc:
                await vc.disconnect()
                self.middlequeues[str(guild_id)] = []
                await asyncio.sleep(0.5)
            channel = guild.get_channel(vc_id)
            try:
                await channel.connect(cls=CustomPlayer())
            except ClientException as e:
                print(e)
                continue
            else:
                break

    async def leave_vc(self, guild_id, vc_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            await vc.disconnect()
            self.middlequeues[str(guild_id)] = []

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
            await action(search, vc, self.middlequeues)
        else:
            # handle text input
            await ctx.send("Idk that link is suss. Try again.")
            

    @commands.command()
    async def pause(self, ctx):
        """Pauses the current song"""
        vc = ctx.voice_client
        if vc:
            if vc.playing and not vc.paused:
                await vc.pause(True)
            else:
                await ctx.send("Nothing is playing.")
        else:
            await ctx.send("The bot is not connected to a voice channel")

    @commands.command()
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
