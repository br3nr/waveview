import asyncio
import json
import uuid
from fastapi.encoders import jsonable_encoder as jsonify
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket
from fastapi.responses import RedirectResponse, JSONResponse
from src.music.music_player import Music
from config import (
    REDIRECT_URI,
    REDIRECT_LOC,
)
from zenora import APIClient


class BotAPI:
    def __init__(self, bot, token, client_secret):
        self.app = FastAPI(debug=True)
        self.api_client = APIClient(token, client_secret=client_secret)
        self.bot = bot
        self.session = {}
        self.file_path = "session.json"

        try:
            with open(self.file_path, "r") as file:
                self.session = json.load(file)
        except FileNotFoundError:
            self.session = {}

        self.app.get("/auth/redirect")(self.callback)
        self.app.get("/auth/login/{session_id}")(self.login)
        self.app.websocket("/ws")(self.ws)(self.ws)
        self.app.get("/get_servers/{user_id}")(self.get_servers)
        self.app.get("/remove_track/{guild_id}/{track_id}")(self.remove_track)
        self.app.get("/get_servers/{user_id}")(self.get_servers)
        self.app.get("/get_vc/{guild_id}")(self.get_vc)
        self.app.get("/join_vc/{guild_id}/{vc_id}")(self.join_vc)
        self.app.post("/play_song/{guild_id}")(self.play_song)
        self.app.get("/playing/{guild_id}")(self.playing)
        self.app.get("/pause/{guild_id}")(self.pause)
        self.app.get("/thumbnail/{guild_id}")(self.thumbnail)
        self.app.get("/skip/{guild_id}")(self.skip)
        self.app.get("/resume/{guild_id}")(self.resume)
        self.app.get("/seek/{guild_id}/{time}")(self.seek)

    async def callback(self, code: str):
        global session
        access_token = self.api_client.oauth.get_access_token(
            code, REDIRECT_URI
        ).access_token

        bearer_client = APIClient(access_token, bearer=True)
        current_user = bearer_client.users.get_current_user()

        user = {
            "id": str(current_user.id),
            "discriminator": str(current_user.discriminator),
            "name": str(current_user.username),
            "avatar_url": str(current_user.avatar_url),
            "username": str(current_user.username),
            "access_token": str(access_token),  # may need to remove for security
        }

        session_id = str(uuid.uuid4())

        while session_id in self.session:  # make sure the uuid is unique
            session_id = str(uuid.uuid4())

        self.session[session_id] = user

        with open(self.file_path, "w") as file:
            json.dump(self.session, file)

        response = RedirectResponse(REDIRECT_LOC)
        response.set_cookie("session_id", session_id)

        return response

    async def login(self, session_id: str, response: Response):
        if session_id in self.session.keys():
            return JSONResponse(content=self.session[session_id])

        response.status_code = 401
        return response

    async def ws(self, websocket: WebSocket):
        await websocket.accept()
        music_cls = Music(self.bot)
        while True:
            await asyncio.sleep(0.1)  # Sleep for 0.1 seconds
            guild_tracks = {}
            for guild in self.bot.guilds:
                music_player = music_cls.get_player(guild.id)
                if music_player is not None:
                    track_info = await self.get_track_info(music_player.current)
                    queue_list = music_cls.get_queue(str(guild.id))
                    json_queue = await self.get_queue_json(queue_list)
                    guild_tracks[str(guild.id)] = {
                        "title": track_info["title"],
                        "thumbnail": track_info["thumbnail"],
                        "position": music_player.position,
                        "length": track_info["length"],
                        "queue": json_queue,
                    }
                else:
                    guild_tracks[str(guild.id)] = self.get_default_guild_track_data()
            await self.send_guild_tracks(guild_tracks, websocket)

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

    async def remove_track(self, guild_id, track_id):
        try:
            await Music(self.bot).dequeue_track_by_id(guild_id, track_id)
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
        await Music(self.bot).join_vc(int(guild_id), int(vc_id))
        return "Success"

    async def play_song(self, guild_id: str, request: Request):
        try:
            data = await request.json()
            url = data.get("url")
            print(f"Playing song: {url} in guild: {guild_id}")
            await Music(self.bot).play_song_by_query(guild_id, url)
            return {"message": "Ok"}
        except IndexError:
            print(f"IndexError in remove_track. Calling track id: {url}")
            return {"error": "500 Internal Server Error"}

    async def playing(self, guild_id):
        try:
            music_player = Music(self.bot).get_player(guild_id)

            if hasattr(music_player, "thumbnail"):
                thumbnail_url = music_player.thumbnail
            else:
                thumbnail_url = music_player.images[0]
            return jsonify(
                {"title": music_player.current.title, "thumbnail": thumbnail_url}
            )

        except AttributeError:
            raise HTTPException(status_code=500, detail="Server bronk")

    async def pause(self, guild_id: str):
        await Music(self.bot).pause_track(guild_id)
        return {"message": "OK"}

    async def skip(self, guild_id: str):
        await Music(self.bot).skip_track(guild_id)
        return {"message": "OK"}

    async def resume(self, guild_id: str):
        await Music(self.bot).resume_track(guild_id)
        return {"message": "OK"}

    async def seek(self, guild_id: str, time: str):
        await Music(self.bot).seek_track(guild_id, time)
        return {"message": "OK"}

    async def thumbnail(self, guild_id: str):
        try:
            thumbnail = await Music(self.bot).get_thumbnail(guild_id)
            return {"thumbnailUrl": thumbnail}
        except AttributeError:
            return {"error": "500 Internal Server Error"}

    async def get_track_info(self, music_player):
        if music_player is None:
            return self.get_default_guild_track_data()
        else:
            if hasattr(music_player, "thumbnail"):
                thumbnail_url = await music_player.fetch_thumbnail()
            else:
                thumbnail_url = music_player.images[0]
        
            track_title = music_player.title
            return {"title": track_title, "thumbnail": thumbnail_url, "length": music_player.length}

    async def get_queue_json(self, queue_list):
        json_queue = []
        for i in range(len(queue_list)):
            track_uuid = queue_list[i].uuid
            track_title = queue_list[i].track.title
            try:
                if queue_list[i].thumbnail_uri is not None:
                    thumbnail_url = queue_list[i].thumbnail_uri
                else:
                    thumbnail_url = await queue_list[i].track.fetch_thumbnail()
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

    async def send_guild_tracks(self, guild_tracks, websocket):
        await websocket.send_json(guild_tracks)
