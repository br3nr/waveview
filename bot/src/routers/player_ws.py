from fastapi import APIRouter
from fastapi import WebSocket
from websockets.exceptions import ConnectionClosedError
from fastapi import WebSocket
import asyncio


class PlayerWebsocket(APIRouter):
    def __init__(self, bot, music_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.music_cls = music_cls
        self.configure_routes()

    def configure_routes(self):
        self.add_api_websocket_route("/ws", self.ws)

    async def ws(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            try:
                await asyncio.sleep(0.1)  # Sleep for 0.1 seconds
                guild_tracks = {}
                for guild in self.bot.guilds:
                    music_player = self.music_cls.get_player(guild.id)
                    if music_player is not None:
                        track_info = await self.get_track_info(music_player.current)
                        queue_list = self.music_cls.get_queue(str(guild.id))
                        json_queue = await self.get_queue_json(queue_list)
                        guild_tracks[str(guild.id)] = {
                            "title": track_info["title"],
                            "thumbnail": track_info["thumbnail"],
                            "position": music_player.position,
                            "length": track_info["length"],
                            "queue": json_queue,
                        }
                    else:
                        guild_tracks[
                            str(guild.id)
                        ] = self.get_default_guild_track_data()
                await websocket.send_json(guild_tracks)
            except TypeError as e:
                print("TypeError in ws: ", e)
                pass
            except ConnectionClosedError:
                print("Websocket unexpectedly closed.")
                await websocket.close()
                break

    async def get_track_info(self, music_player):
        if music_player is None:
            return self.get_default_guild_track_data()
        else:
            if hasattr(music_player, "thumbnail"):
                thumbnail_url = await music_player.fetch_thumbnail()
            else:
                thumbnail_url = music_player.images[0]

            track_title = music_player.title
            return {
                "title": track_title,
                "thumbnail": thumbnail_url,
                "length": music_player.length,
            }

    async def get_queue_json(self, queue_list):
        json_queue = []
        tmp_list = queue_list.copy()
        for i in range(len(tmp_list)):
            track_uuid = tmp_list[i].uuid
            track_title = tmp_list[i].track.title
            try:
                if tmp_list[i].thumbnail_uri is not None:
                    thumbnail_url = tmp_list[i].thumbnail_uri
                else:
                    thumbnail_url = await tmp_list[i].track.fetch_thumbnail()
            except AttributeError:
                thumbnail_url = None

            json_queue.append(
                {
                    "id": i,
                    "uuid": track_uuid,
                    "title": track_title,
                    "thumbnail": thumbnail_url,
                }
            )
        return json_queue

    def get_default_guild_track_data(self):
        return {
            "title": "No track playing",
            "thumbnail": None,
            "length": 0,
            "position": 0,
            "queue": [],
        }
