from typing import Optional

from server.game.device import FakeWAMClient
from server.game.errors import ImproperSessionPlayers


class UIController:

    def __init__(self, logger, *, app = None, gameManager=None):
        # Bind UI engine in here.
        self.logger = logger
        self.app = app
        self.game_manager = gameManager
        logger.debug('Created UIController interface.')

    # Bind objects

    def bind_app(self, app):
        if self.app:
            raise ValueError('UIController.app is already bound!')
        self.app = app

    def bind_game_manager(self, gameManager):
        if self.game_manager:
            raise ValueError('UIController.game_manager is already bound!')
        self.game_manager = gameManager

    # Control Game
    @property
    def is_running(self) -> bool:
        return self.game_manager.current_session is not None

    def start_game(self):
        if self.is_running:
            # TODO : Consider ignore `start_game` task instead of raising Exception and breaking process.
            raise ValueError('GameSession is already running')
        self.logger.info('Create new game session.')
        session = self.game_manager.create_session()
        self.logger.info('Start game session.')
        session.run()

    def start_test_game(self):
        if self.is_running:
            # TODO : Consider ignore `start_game` task instead of raising Exception and breaking process.
            raise ValueError('GameSession is already running')
        self.logger.info('Create new Test game session.')
        self.write_text('두더지 배틀 게임 (TEST) 의 세션을 생성중입니다...')
        self.game_manager.clients = [
            FakeWAMClient(name='Player0', port='FakeSerialPort/0', clientNumber=0),
            FakeWAMClient(name='Player1', port='FakeSerialPort/1', clientNumber=1)
        ]
        self.write_text('두더지 배틀 게임 (TEST) 에 사용될 FakeWAMClient 객체를 생성했습니다.')
        session = self.game_manager.create_session()
        self.logger.info('Start test game session.')
        self.write_text('두더지 배틀 게임 (TEST) 의 세션을 생성했습니다.')
        session.run()
        self.write_text('두더지 배틀 게임 (TEST) 의 세션을 시작합니다.')

    def stop_game(self):
        if not self.is_running:
            # TODO : Consider ignore `stop_game` task instead of raising Exception and breaking process.
            raise ValueError('GameSession is not running')

        self.game_manager.current_session.shutdown()

    # Control Window
    def write_text(self, text: str):
        self.app.write_event_log(text)

    def update_game_info(self, gameInfo):
        """
        Update ui using gameInfo.
        :param gameInfo: game.GameInfo object containing game's information.
        """
        pass

    def handle_game_finish(self):
        self.app.main_box.control.set_btn_green()
