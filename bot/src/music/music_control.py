from discord.ext import commands
import wavelink
from wavelink.ext import spotify
import os
from log import log_command
from discord import ClientException
import asyncio
from .custom_player import CustomPlayer
from .music_utils import check_string
from .music_players import *


class Music(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.song_queue = {}
        self.cid = os.environ["SPOTIFY_CLIENT_ID"]
        self.csecret = os.environ["SPOTIFY_CLIENT_SECRET"]
        self.middlequeues = {}
        # for each guild, create a middlequeue
        for guild in self.bot.guilds:
            self.middlequeues[str(guild.id)] = []

        # Map URL types to their corresponding functions
        self.url_type_mapping = {
            "Spotify Track": SpotifyPlayer().play_track,
            "Spotify Playlist": SpotifyPlayer().play_playlist,
            "Spotify Album": SpotifyPlayer().play_playlist,
            "YouTube Song": YoutubePlayer().play_track,
            "YouTube Playlist": YoutubePlayer().play_playlist,
            "Text": YoutubePlayer().play,
        }
    
    def initialise_player(self):
        self.bot.loop.create_task(self.connect_nodes())

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
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
        await self.bot.wait_until_ready()
        sc = spotify.SpotifyClient(client_id=self.cid, client_secret=self.csecret)
        node: wavelink.Node = wavelink.Node(
            uri="http://localhost:2333", password="1234"
        )
        await wavelink.NodePool.connect(client=self.bot, nodes=[node], spotify=sc)

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
            print(self.middlequeues)
            await action(query, vc, self.middlequeues)

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
