from models import GameSession, User, Controller


class GameHandler:
    """

    """
    def __init__(self, server):
        """
        Initialize game handler
        Args:
             server (sanic.Sanic) : Sanic app object.
        """
        self.server = server
