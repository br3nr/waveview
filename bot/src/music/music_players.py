import discord
import wavelink
from wavelink.ext import spotify
from .custom_player import CustomPlayer
from .music_utils import check_string
import re
from abc import ABC, abstractmethod
import uuid


class MiddleQueue:
    def __init__(self, track, thumbnail_uri=None):
        self.uuid = str(uuid.uuid4())
        self.track = track
        self.thumbnail_uri = thumbnail_uri


class MusicPlayer(ABC):
    @abstractmethod
    def play_track(self, track: str, vc: CustomPlayer):
        pass

    @abstractmethod
    def play_playlist(self, track: str, vc: CustomPlayer):
        pass

    async def play(self, search: str, vc: CustomPlayer, middlequeues):
        # convert query to youtube url
        tracks = await wavelink.YouTubeTrack.search(search)
        # TODO: Error check
        track = tracks[0]
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            guild_id = str(vc.guild.id)
            cur_queue = middlequeues.setdefault(guild_id, [])
            cur_queue.append(MiddleQueue(track))
            middlequeues[guild_id] = cur_queue
        else:
            await vc.play(track)
        return middlequeues


class YoutubePlayer(MusicPlayer):
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


class SpotifyPlayer(MusicPlayer):
    async def play_track(self, track: str, vc: CustomPlayer, middlequeues):
        track = await spotify.SpotifyTrack.search(query=track)
        if vc.is_playing() or not vc.queue.is_empty:
            vc.queue.put(item=track)
            guild_id = str(vc.guild.id)
            cur_queue = middlequeues.get(guild_id, [])
            cur_queue.append(MiddleQueue(track, track.images[-1]))
            middlequeues[str(guild_id)] = cur_queue
        else:
            await vc.play(track)

    async def play_playlist(self, playlist: str, vc: CustomPlayer, middlequeues):
        async for track in spotify.SpotifyTrack.iterator(query=playlist):
            if vc.is_playing() or not vc.queue.is_empty:
                vc.queue.put(item=track)
                guild_id = str(vc.guild.id)
                cur_queue = middlequeues.get(guild_id, [])
                cur_queue.append(MiddleQueue(track, track.images[-1]))
                middlequeues[str(guild_id)] = cur_queue
            else:
                await vc.play(track)
