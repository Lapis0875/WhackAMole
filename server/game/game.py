from typing import Optional
from .device import WhackAMoleClient
from .game_data import GameClientData, GameServerData
from .game_object import Player, GameInfo, GameSession


class GameManager:
    current_session: Optional[GameSession]
    clients: list[WhackAMoleClient]

    def __init__(self, logger, *, ui=None):
        self.logger = logger
        logger.info('Initializing GameManager instance...')
        self.current_session = None
        logger.info('GameManager >>> Connecting Whack A Mole Clients')
        self.clients = WhackAMoleClient.search()
        logger.info(f'GameManager >>> Connected {len(self.clients)} clients.')
        self.ui = ui
        ui.bind_game_manager(self)
        logger.info('GameManager >>> Bind UI Controller interface.')

    def create_session(self) -> 'GameSession':
        self.logger.info('GameManager >>> Create new session.')
        session = GameSession.create(gameManager=self)
        return session

    def write_event_log(self, text: str = None):
        self.ui.write_text(text)

    def write_error_log(self, e: Exception, extra_text: str = None):
        text = str(e) + '\n'
        if extra_text:
            text += extra_text + '\n'
        self.ui.write_text(text)

    def display_game_screen(self):
        pass

    def update_screen(self, gameInfo: GameInfo = None):
        self.logger.debug('Update screen.')
        self.ui.update_game_info(gameInfo or self.current_session.gameInfo)

    def show_result(self, gameInfo: GameInfo = None):
        self.logger.debug('Show game result screen.')
        self.ui.update_game_info(gameInfo or self.current_session.gameInfo)
        self.current_session = None
