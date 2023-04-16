import wavelink

class CustomPlayer(wavelink.Player):
    """Custom player class for wavelink."""
    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()