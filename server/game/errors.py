class GameError(Exception):
    """Base class for all game errors"""


class ImproperSessionPlayers(GameError):
    """Raised when session has improper players."""
    def __init__(self, session):
        self._session = session
        super(ImproperSessionPlayers, self).__init__(f'GameSession {session.__session_name__} has improper players : {len(session.players)} players connected.')
