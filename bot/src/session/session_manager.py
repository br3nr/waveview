import uuid

class SessionManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.sessions = {}
        pass
    
    def is_authenticated(self, session_id):
        if session_id in self.sessions.keys():
            return True
        return False
    
    def create_session(self, user):
        session_id = str(uuid.uuid4())
        while session_id in self.sessions:
            session_id = str(uuid.uuid4())
        self.sessions[session_id] = user
        return session_id

    def get_user(self, session_id):
        return self.sessions[session_id]