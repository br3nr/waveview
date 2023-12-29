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

        # Map URL types to their corresponding functions
        self.url_type_mapping = {
            #"Spotify Track": SpotifyPlayer().play_track,
            #"Spotify Playlist": SpotifyPlayer().play_playlist,
            #"Spotify Album": SpotifyPlayer().play_playlist,
            #"YouTube Song": YoutubePlayer().play_track,
            #"YouTube Playlist": YoutubePlayer().play_playlist,
            #"Text": YoutubePlayer().play,
        }
    
    def initialise_player(self):
        self.bot.loop.create_task(self.connect_nodes())

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if not player.queue.is_empty:
            guild_id = player.guild.id
            cur_queue = self.middlequeues[str(guild_id)].pop(0)
            self.middlequeues[guild_id] = cur_queue
            next_track = player.queue.get()
            await player.play(next_track)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f"Node: <{node.identifier}> is ready!")

    async def connect_nodes(self):
        nodes = [wavelink.Node(uri=self.lavalink_uri, password="1234")]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)
    
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
        guild = self.bot.get_guild(int(guild_id))
        vc = guild.voice_client
        if vc:
            if len(vc.queue) == 0:
                print("AAAAAA")
                return await vc.stop()
            print(type(vc)) 
            return await vc.skip()

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

        #player = wavelink.Node.get_player(guild_id)
        player = vc
        #url_type = check_string(query)control
        #action = self.url_type_mapping.get(url_type, None)
        #if action:
        #    await action(query, vc, self.middlequeues)
        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            return # no tracks
        
        cur_queue = self.middlequeues.get(guild_id, [])

        if isinstance(tracks, wavelink.Playlist):
            # BUG: possible bug if len of player.queue is never 0
            a = 1
        else:
            track: wavelink.Playable = tracks[0]
            if player.playing or not len(player.queue) == 0:
                print("Adding song to queue")
                cur_queue.append(MiddleQueue(track))
                await player.queue.put_wait(track)
            else:
                await player.play(track)
        self.middlequeues[guild_id] = cur_queue
        print(self.middlequeues[guild_id])
    """
    async def play_track(self, query: str, vc: CustomPlayer, middlequeues):
        # remove time from youtube link
        query = re.sub(r"&t=\d+", "", query)
        tracks = await wavelink.NodePool.get_node().get_tracks(
            wavelink.YouTubeTrack, query
        )
        track = tracks[0]
        guild_id = str(vc.guild.id)
        cur_queue = middlequeues.get(guild_id, [])
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            cur_queue.append(MiddleQueue(track))
        else:
            await vc.play(track)
        middlequeues[guild_id] = cur_queue

    async def play_playlist(self, query: str, vc: CustomPlayer, middlequeues):
        # Plays a yt playlist
        # TODO: Make this fast
        playlist = await wavelink.NodePool.get_node().get_playlist(
            wavelink.YouTubePlaylist, query
        )
        tracks = playlist.tracks
        guild_id = str(vc.guild.id)
        cur_queue = middlequeues.get(guild_id, [])
        for track in tracks:
            print(track)
            if vc.is_playing() or not vc.queue.is_empty:
                vc.queue.put(item=track)
                cur_queue.append(MiddleQueue(track))
            else:
                await vc.play(track)
            middlequeues[guild_id] = cur_queue
    """

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
