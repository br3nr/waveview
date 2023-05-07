import asyncio
import json
import uuid
from fastapi.encoders import jsonable_encoder as jsonify
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket
from fastapi.responses import RedirectResponse, JSONResponse
from src.music.music_control import Music
from config import REDIRECT_URI, REDIRECT_LOC, TOKEN, CLIENT_SECRET
from zenora import APIClient
from websockets.exceptions import ConnectionClosedError


app = FastAPI(debug=True)
api_client = APIClient(TOKEN, client_secret=CLIENT_SECRET)
session = {}
file_path = "session.json"

try:
    with open(file_path, "r") as file:
        session = json.load(file)
except FileNotFoundError:
    session = {}


@app.get("/auth/redirect")
async def redirect(code: str):
    global session
    access_token = api_client.oauth.get_access_token(
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

    while session_id in session:  # make sure the uuid is unique
        session_id = str(uuid.uuid4())

    session[session_id] = user

    with open(file_path, "w") as file:
        json.dump(session, file)

    response = RedirectResponse(REDIRECT_LOC)
    response.set_cookie("session_id", session_id)

    return response


@app.get("/auth/login/{session_id}")
async def login(session_id: str, response: Response):
    if session_id in session.keys():
        return JSONResponse(content=session[session_id])

    response.status_code = 401
    return response


app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    music_cls = Music()
    while True:
        try:
            await asyncio.sleep(0.1)  # Sleep for 0.1 seconds
            guild_tracks = {}
            for guild in bot.guilds:
                music_player = music_cls.get_player(guild.id)
                if music_player is not None:
                    track_info = await get_track_info(music_player.current)
                    queue_list = music_cls.get_queue(str(guild.id))
                    json_queue = await get_queue_json(queue_list)
                    guild_tracks[str(guild.id)] = {
                        "title": track_info["title"],
                        "thumbnail": track_info["thumbnail"],
                        "position": music_player.position,
                        "length": track_info["length"],
                        "queue": json_queue,
                    }
                else:
                    guild_tracks[str(guild.id)] = get_default_guild_track_data()
            await send_guild_tracks(guild_tracks, websocket)
        except TypeError as e:
            print("TypeError in ws: ", e)
            pass
        except ConnectionClosedError:
            print("Websocket unexpectedly closed.")
            await websocket.close()
            break


app.get("/get_servers/{user_id}")


async def get_servers(user_id):
    active_servers = bot.guilds
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


@app.get("/remove_track/{guild_id}/{track_id}")
async def remove_track(guild_id, track_id):
    try:
        await Music(bot).dequeue_track_by_id(guild_id, track_id)
        return "Ok"
    except IndexError:
        ("IndexError in remove_track. Calling track id: " + track_id)
        raise HTTPException(status_code=404, detail="Track not found")


@app.get("/get_servers/{user_id}")
async def get_servers(user_id):
    active_servers = bot.guilds
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


@app.get("/get_vc/{guild_id}")
async def get_vc(guild_id):
    guild = bot.get_guild(int(guild_id))
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


@app.get("/join_vc/{guild_id}/{vc_id}")
async def join_vc(guild_id, vc_id):
    print("Joining vc: " + vc_id + " in guild: " + guild_id + "")
    await Music(bot).join_vc(int(guild_id), int(vc_id))
    return "Success"


@app.get("/leave_vc/{guild_id}/{vc_id}")
async def leave_vc(guild_id, vc_id):
    print("Leaving vc: " + vc_id + " in guild: " + guild_id + "")
    await Music(bot).leave_vc(int(guild_id), int(vc_id))
    return "Success"


@app.post("/play_song/{guild_id}")
async def play_song(guild_id: str, request: Request):
    try:
        data = await request.json()
        url = data.get("url")
        print(f"Playing song: {url} in guild: {guild_id}")
        await Music(bot).play_song_by_query(guild_id, url)
        return {"message": "Ok"}
    except IndexError:
        print(f"IndexError in remove_track. Calling track id: {url}")
        return {"error": "500 Internal Server Error"}
    except AttributeError:
        raise HTTPException(
            status_code=500, detail="You need to connected to a voice channel first."
        )


@app.get("/playing/{guild_id}")
async def playing(guild_id):
    try:
        music_player = Music(bot).get_player(guild_id)

        if hasattr(music_player, "thumbnail"):
            thumbnail_url = music_player.thumbnail
        else:
            thumbnail_url = music_player.images[0]
        return jsonify(
            {"title": music_player.current.title, "thumbnail": thumbnail_url}
        )

    except AttributeError:
        raise HTTPException(status_code=500, detail="Server bronk")


@app.get("/pause/{guild_id}")
async def pause(guild_id: str):
    await Music(bot).pause_track(guild_id)
    return {"message": "OK"}


@app.get("/skip/{guild_id}")
async def skip(guild_id: str):
    await Music(bot).skip_track(guild_id)
    return {"message": "OK"}


@app.get("/resume/{guild_id}")
async def resume(guild_id: str):
    await Music(bot).resume_track(guild_id)
    return {"message": "OK"}


@app.get("/seek/{guild_id}/{time}")
async def seek(guild_id: str, time: str):
    await Music(bot).seek_track(guild_id, time)
    return {"message": "OK"}


@app.get("/reorder/{guild_id}/{time}/{new_position}")
async def reorder(guild_id: str, time: str, new_position: int):
    await Music(bot).reorder_queue(guild_id, time, new_position)
    return {"message": "OK"}


@app.get("/delete_queue/{guild_id}")
async def delete_queue(guild_id):
    await Music(bot).delete_queue_by_guild(guild_id)
    return {"message": "OK"}


@app.get("/thumbnail/{guild_id}")
async def thumbnail(guild_id: str):
    try:
        thumbnail = await Music(bot).get_thumbnail(guild_id)
        return {"thumbnailUrl": thumbnail}
    except AttributeError:
        return {"error": "500 Internal Server Error"}


async def get_track_info(music_player):
    if music_player is None:
        return get_default_guild_track_data()
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


async def get_queue_json(queue_list):
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


async def send_guild_tracks(guild_tracks, websocket):
    await websocket.send_json(guild_tracks)
