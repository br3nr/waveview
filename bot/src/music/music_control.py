from discord.ext import commands
import wavelink

# from wavelink.ext import spotify
import os
import uuid
from src.logger.log import log_command
from discord import ClientException
import asyncio
from .custom_player import CustomPlayer
from .music_utils import check_string
from typing import cast
from discord import Guild
from typing import List


class MiddleQueue:
    """Middlequeue is a wavelink Queue clone that allows us to swap queue items """
    def __init__(self, track, thumbnail_uri=None):
        self.uuid = str(uuid.uuid4())
        self.track = track
        self.thumbnail_uri = thumbnail_uri


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot, spotify_id, spotify_secret, lavalink_uri):
        self.bot = bot
        self.cid = spotify_id
        self.csecret = spotify_secret
        self.middlequeues = {}
        self.lavalink_uri = lavalink_uri
        # for each guild, create a middlequeue
        for guild in self.bot.guilds:
            self.middlequeues[str(guild.id)] = []

    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self, payload: wavelink.TrackStartEventPayload
    ) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # TODO: Edge cases
            return
        elif player.guild:
            await player.pause(False)
            guild_id: int = player.guild.id
            cur_queue = self.middlequeues[str(guild_id)].pop(0)
            self.middlequeues[guild_id] = cur_queue

    async def setup_hook(self) -> None:
        nodes = [wavelink.Node(uri=self.lavalink_uri, password="1234")]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)

    def initialise_player(self):
        self.bot.loop.create_task(self.setup_hook())

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node: <{node.identifier}> is ready!")

    def get_queue(self, guild_id) -> List:
        if guild_id in self.middlequeues:
            return self.middlequeues[guild_id]
        else:
            return []

    async def dequeue_track_by_id(self, guild_id, track_id):
        guild: Guild | None = self.bot.get_guild(int(guild_id))
        if guild:
            player = cast(wavelink.Player, guild.voice_client)
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

            player.queue = wavelinkQueue
            self.middlequeues[guild_id] = cur_queue

    async def reorder_queue(self, guild_id: int, uuid: int, new_position: int) -> None:
        guild: Guild | None = self.bot.get_guild(int(guild_id))
        if guild:
            player = cast(wavelink.Player, guild.voice_client)
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

            player.queue = wavelinkQueue

    async def delete_queue_by_guild(self, guild_id):
        guild: Guild | None = self.bot.get_guild(int(guild_id))
        if guild:
            player = cast(wavelink.Player, guild.voice_client)
            player.queue.clear()
            self.middlequeues[guild_id] = []

    def get_player(self, guild_id) -> wavelink.Player | None:
        guild = self.bot.get_guild(int(guild_id))
        if guild:
            player = cast(wavelink.Player, guild.voice_client)
            return player
        return None

    async def pause_track(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            return

        player = cast(wavelink.Player, guild.voice_client)
        if not player:
            return
        await player.pause(True)

    async def resume_track(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            return

        player = cast(wavelink.Player, guild.voice_client)
        if not player:
            return
        await player.pause(False)

    async def skip_track(self, guild_id):
        guild: Guild | None = self.bot.get_guild(int(guild_id))

        if guild:
            vc = guild.voice_client
            player: wavelink.Player = cast(wavelink.Player, vc)
            if player:
                if len(player.queue) == 0:
                    await player.stop()
                else:
                    await player.skip(force=True)

    async def seek_track(self, guild_id, seek_time):
        guild: Guild | None = self.bot.get_guild(int(guild_id))
        player = cast(wavelink.Player, guild.voice_client)
        await player.seek(seek_time)
 
    def get_guilds(self):
        return self.bot.guilds

    async def play_song_by_query(self, guild_id, query):
        guild: Guild | None = self.bot.get_guild(int(guild_id))
        player = cast(wavelink.Player, guild.voice_client)  # type: ignore

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
        guild: Guild | None = self.bot.get_guild(int(guild_id))
        player = cast(wavelink.Player, guild.voice_client)
        if player:
            await player.disconnect()
            self.middlequeues[str(guild_id)] = []
 
