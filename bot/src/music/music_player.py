import discord
from discord.ext import commands
import wavelink
from wavelink.ext import spotify
import os
from log import log_command
from discord import ClientException
import asyncio
from .custom_player import CustomPlayer
from .middle_queue import MiddleQueue
from .music_utils import check_string
import re


class Music(commands.Cog):
    """Suite of commands allowing BrennerBot to play music from Youtube and Spotify."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, bot: commands.Bot):
        if hasattr(self, "initialized"):
            return
        self.initialized = True

        self.bot = bot
        self.song_queue = {}
        self.cid = os.environ["SPOTIFY_CLIENT_ID"]
        self.csecret = os.environ["SPOTIFY_CLIENT_SECRET"]
        self.current_track = None
        bot.loop.create_task(self.connect_nodes())
        self.middlequeues = {}
        # for each guild, create a middlequeue
        for guild in self.bot.guilds:
            self.middlequeues[str(guild.id)] = []

        # Map URL types to their corresponding functions
        self.url_type_mapping = {
            "Spotify Track": self.play_spotify_track,
            "Spotify Playlist": self.play_spotify_playlist,
            "Spotify Album": self.play_spotify_playlist,
            "YouTube Song": self.play_youtube_song,
            "YouTube Playlist": self.play_youtube_playlist,
            "Text": self.play_query,
        }

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player = payload.player
        if not player.queue.is_empty:
            guild_id = player.guild.id
            cur_queue = self.middlequeues[str(guild_id)].pop(0)
            self.middlequeues[guild_id] = cur_queue
            next_track = player.queue.get()
            self.current_track = next_track
            await player.play(next_track)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f"Node: <{node.identifier}> is ready!")

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()
        sc = spotify.SpotifyClient(client_id=self.cid, client_secret=self.csecret)
        node: wavelink.Node = wavelink.Node(
            uri="http://localhost:2333", password="1234"
        )
        await wavelink.NodePool.connect(client=self.bot, nodes=[node], spotify=sc)

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
        """
        Play requested song (url or query). Queues if a song is already playing.

        Usage:
        !play <search>
        """
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

    def get_queue(self, guild_id):
        if guild_id in self.middlequeues:
            return self.middlequeues[guild_id]
        else:
            return []

    def get_current_song(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        if guild is None:
            return "Server not found"
        vc = guild.voice_client
        if vc.is_playing():
            return vc.current

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
            print(cur_queue[i].uuid, uuid)
            if cur_queue[i].uuid == uuid:
                track = cur_queue[i]
                del cur_queue[i]
                cur_queue.insert(new_position, track)
                break

        wavelinkQueue = wavelink.Queue()
        for i in range(len(cur_queue)):
            wavelinkQueue.put(cur_queue[i].track)

        guild.voice_client.queue = wavelinkQueue

    def get_player(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        return vc

    async def pause_track(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            if vc.is_playing() and not vc.is_paused():
                await vc.pause()

    async def resume_track(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            if vc.is_paused():
                await vc.resume()

    async def skip_track(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            if vc.queue.is_empty:
                return await vc.stop()
            await vc.seek(vc.current.length * 1000)
            if vc.is_paused():
                await vc.resume()

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
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        return vc.current.thumbnail

    def get_guilds(self):
        return self.bot.guilds

    async def play_song_by_query(self, guild_id, query):
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        url_type = check_string(query)
        action = self.url_type_mapping.get(url_type, None)
        if action:
            await action(None, query, vc)

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

    async def play_query(
        self, ctx: discord.ext.commands.Context, search: str, vc: CustomPlayer
    ):
        # convert query to youtube url
        track = await wavelink.YouTubeTrack.search(search, return_first=True)
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            guild_id = str(vc.guild.id)
            cur_queue = self.middlequeues[guild_id]
            cur_queue.append(MiddleQueue(track))
            self.middlequeues[guild_id] = cur_queue
            if ctx is not None:
                await ctx.send(
                    embed=discord.Embed(
                        title=track.title,
                        url=track.uri,
                        description=f"Queued {track.title} in {vc.channel}",
                    )
                )
        else:
            await vc.play(track)
            self.current_track = track
            if ctx is not None:
                await ctx.send(
                    embed=discord.Embed(
                        title=vc.current.title,
                        url=vc.current.uri,
                        description=f"Playing {vc.current.title} in {vc.channel}",
                    )
                )

    async def play_spotify_track(
        self, ctx: discord.ext.commands.Context, track: str, vc: CustomPlayer
    ):
        track = await spotify.SpotifyTrack.search(query=track)
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            guild_id = str(vc.guild.id)
            cur_queue = self.middlequeues.get(guild_id, [])
            cur_queue.append(MiddleQueue(track))
            self.middlequeues[guild_id] = cur_queue
            if ctx is not None:
                await ctx.send(
                    embed=discord.Embed(
                        title=track.title,
                        url=track.uri,
                        description=f"Queued {track.title} in {vc.channel}",
                    )
                )
        else:
            await vc.play(track)
            self.current_track = track
            if ctx is not None:
                await ctx.send(
                    embed=discord.Embed(
                        title=track.title,
                        url=track.uri,
                        description=f"Queued {track.title} in {vc.channel}",
                    )
                )

    async def play_spotify_playlist(
        self, ctx: discord.ext.commands.Context, playlist: str, vc: CustomPlayer
    ):
        async for partial in spotify.SpotifyTrack.iterator(query=playlist):
            if vc.is_playing() or not vc.queue.is_empty:
                vc.queue.put(item=partial)
                guild_id = str(vc.guild.id)
                cur_queue = self.middlequeues.get(guild_id, [])
                cur_queue.append(MiddleQueue(partial, partial.images[-1]))
                self.middlequeues[str(guild_id)] = cur_queue
            else:
                await vc.play(partial)
                self.current_track = partial
                if ctx is not None:
                    await ctx.send(
                        embed=discord.Embed(
                            title=vc.current.title,
                            description=f"Playing {vc.current.title} in {vc.channel}",
                        )
                    )

    async def play_youtube_song(
        self, ctx: discord.ext.commands.Context, query: str, vc: CustomPlayer
    ):
        # remove time from youtube link
        query = re.sub(r"&t=\d+", "", query)
        track = await wavelink.NodePool.get_node().get_tracks(
            wavelink.YouTubeTrack, query
        )
        track = track[0]
        guild_id = ctx.guild.id
        cur_queue = self.middlequeues.get(guild_id, [])
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            cur_queue.append(MiddleQueue(track))
            if ctx is not None:
                await ctx.send(
                    embed=discord.Embed(
                        title=track.title,
                        url=track.uri,
                        description=f"Queued {track.title} in {vc.channel}",
                    )
                )
        else:
            await vc.play(track)
            self.current_track = track
            if ctx is not None:
                await ctx.send(
                    embed=discord.Embed(
                        title=vc.current.title,
                        url=vc.current.uri,
                        description=f"Playing {vc.current.title} in {vc.channel}",
                    )
                )
        self.middlequeues[guild_id] = cur_queue

    async def play_youtube_playlist(ctx: discord.ext.commands.Context, playlist: str):
        # play youtube playlist
        pass
