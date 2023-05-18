import json
import uuid
from fastapi import APIRouter
from zenora import APIClient
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi import Response 
from ..session.session_manager import SessionManager

class AuthRouter(APIRouter):

    def __init__(self, token, client_secret, redirect_uri, redirect_loc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = APIClient(token=token, client_secret=client_secret)
        self.session = {}
        self.file_path = "session.json"
        self.redirect_uri = redirect_uri
        self.redirect_loc = redirect_loc
        self.configure_routes()
        self.initialise_session()
        
    def configure_routes(self):
        self.add_api_route("/auth/redirect", self.redirect, methods=["GET"])
        self.add_api_route("/auth/login/{session_id}", self.login, methods=["GET"])
        
    def initialise_session(self):
        try:
            with open(self.file_path, "r") as file:
                self.session = json.load(file)
        except FileNotFoundError:
            self.session = {}

    async def redirect(self, code: str):
        global session
        access_token = self.api_client.oauth.get_access_token(code, self.redirect_uri).access_token

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

        session_manager = SessionManager.get_instance()
        session_id = session_manager.create_session(user)

        response = RedirectResponse(self.redirect_loc)
        response.set_cookie("session_id", session_id)
        return response
    
    async def login(self, session_id: str, response: Response):
        session_manager = SessionManager.get_instance()
        
        if session_manager.is_authenticated(session_id):
            user = session_manager.get_user(session_id)
            return JSONResponse(content=user)

        response.status_code = 401
        return response
