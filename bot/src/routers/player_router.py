import wavelink
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder as jsonify
from fastapi import HTTPException, Request

class PlayerRouter(APIRouter):
    def __init__(self, bot, player, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.player = player
        self.configure_routes()

    def configure_routes(self):
        self.add_api_route("/api/remove_track/{guild_id}/{track_id}", self.remove_track, methods=["GET"])
        self.add_api_route("/api/get_servers/{user_id}", self.get_servers, methods=["GET"])
        self.add_api_route("/api/get_vc/{guild_id}", self.get_vc, methods=["GET"])
        self.add_api_route("/api/join_vc/{guild_id}/{vc_id}", self.join_vc, methods=["GET"])
        self.add_api_route("/api/leave_vc/{guild_id}/{vc_id}", self.leave_vc, methods=["GET"])
        self.add_api_route("/api/play_song/{guild_id}", self.play_song, methods=["POST"])
        self.add_api_route("/api/playing/{guild_id}", self.playing, methods=["GET"])
        self.add_api_route("/api/thumbnail/{guild_id}", self.thumbnail, methods=["GET"])
        self.add_api_route("/api/delete_queue/{guild_id}", self.delete_queue, methods=["GET"])
        self.add_api_route("/api/reorder/{guild_id}/{time}/{new_position}", self.reorder, methods=["GET"])
        self.add_api_route("/api/seek/{guild_id}/{time}", self.seek, methods=["GET"])
        self.add_api_route("/api/resume/{guild_id}", self.resume, methods=["GET"])
        self.add_api_route("/api/pause/{guild_id}", self.pause, methods=["GET"])
        self.add_api_route("/api/skip/{guild_id}", self.skip, methods=["GET"])

    async def remove_track(self, guild_id, track_id):
        try:
            await self.player.dequeue_track_by_id(guild_id, track_id)
            return "Ok"
        except IndexError:
            ("IndexError in remove_track. Calling track id: " + track_id)
            raise HTTPException(status_code=404, detail="Track not found")

    async def get_servers(self, user_id):
        active_servers = self.bot.guilds
        guild_list = []

        for guild in active_servers:
            if guild.get_member(int(user_id)):
                guild_list.append(
                    {
                        "id": str(guild.id),
                        "name": str(guild.name),
                        "icon": str(guild.icon.url),
                    }
                )
        return jsonify(guild_list)

    async def get_vc(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        vc_list = []
        for vc in guild.voice_channels:
            is_connected = False
            if guild.voice_client and guild.voice_client.channel == vc:
                is_connected = True
            vc_list.append(
                {
                    "vc_name": str(vc.name),
                    "vc_id": str(vc.id),
                    "is_connected": is_connected,
                }
            )
        return jsonify(vc_list)

    async def join_vc(self, guild_id, vc_id):
        print("Joining vc: " + vc_id + " in guild: " + guild_id + "")
        await self.player.join_vc(int(guild_id), int(vc_id))
        return "Success"

    async def leave_vc(self, guild_id, vc_id):
        print("Leaving vc: " + vc_id + " in guild: " + guild_id + "")
        await self.player.leave_vc(int(guild_id), int(vc_id))
        return "Success"

    async def play_song(self, guild_id: str, request: Request):
        try:
            data = await request.json()
            url = data.get("url")
            print(f"Playing song: {url} in guild: {guild_id}")
            await self.player.play_song_by_query(guild_id, url)
            return {"message": "Ok"}
        except IndexError:
            print(f"IndexError in remove_track. Calling track id: {url}")
            return {"error": "500 Internal Server Error"}
        except AttributeError:
            raise HTTPException(
                status_code=500,
                detail="You need to connected to a voice channel first.",
            )
        except wavelink.ext.spotify.SpotifyRequestError:
            raise HTTPException(
                status_code=403,
                detail="""Error: Spotify API not set up.
                    Please provide the API key and client ID to enable Spotify integration.
                    Contact the administrator for assistance."""
            )
        except wavelink.exceptions.NoTracksError:
            raise HTTPException(
                status_code=404,
                detail="No tracks found with that query."
            )
            

    async def playing(self, guild_id):
        try:
            music_player = self.player.get_player(guild_id)

            if hasattr(music_player, "thumbnail"):
                thumbnail_url = music_player.thumbnail
            else:
                thumbnail_url = music_player.images[0]
            return jsonify(
                {"title": music_player.current.title, "thumbnail": thumbnail_url}
            )

        except AttributeError:
            raise HTTPException(status_code=500, detail="Server bronk")

    

    async def skip(self, guild_id: str):
        await self.player.skip_track(guild_id)
        return {"message": "OK"}

    async def resume(self, guild_id: str):
        await self.player.resume_track(guild_id)
        return {"message": "OK"}
    
    async def pause(self, guild_id: str, request: Request):
        await self.player.pause_track(guild_id)
        return {"message": "OK"}

    async def seek(self, guild_id: str, time: str):
        await self.player.seek_track(guild_id, time)
        return {"message": "OK"}

    async def reorder(self, guild_id: str, time: str, new_position: int):
        await self.player.reorder_queue(guild_id, time, new_position)
        return {"message": "OK"}

    async def delete_queue(self, guild_id):
        await self.player.delete_queue_by_guild(guild_id)
        return {"message": "OK"}

    async def thumbnail(self, guild_id: str):
        try:
            thumbnail = await self.player.get_thumbnail(guild_id)
            return {"thumbnailUrl": thumbnail}
        except AttributeError:
            return {"error": "500 Internal Server Error"}
