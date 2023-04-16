import uuid


class MiddleQueue:
    def __init__(self, track, thumbnail_uri=None):
        self.uuid = str(uuid.uuid4())
        self.track = track
        self.thumbnail_uri = thumbnail_uri