from __future__ import annotations

import datetime
import enum
import random
import threading

import serial
from typing import Optional, Final, NamedTuple, Callable

from .device import WhackAMoleClient
from .errors import ImproperSessionPlayers
from .game_data import GameClientData, GameServerData


ItemHandler = Callable[['GameSession', 'Player', 'Player'], None]

__all__ = (
    'PanelItem',
    'MAX_HP', 'MIN_HP', 'ATTACK_DAMAGE', 'HEAL_AMOUNT',
    'Player',
    'GameInfo',
    'GameSession'
)


class PanelItem(enum.Enum):
    """
    Game Item Enum :
    this enum represents items which are displayed on mole (Panel which player hits).
    """
    BLANK = 0               # Transparent   : 아무런 아이템도 없는 빈 칸입니다.
    HEAL_SELF = 1           # Green         : 자신을 회복하는 칸입니다.
    OPPONENT_BLOCK = 2      # Purple        : 상대방이 일시적으로 자신을 공격하지 못하게 합니다.
    BLOCKED_TILE = 3        # ?             : OPPONENT_BLOCK 으로 인해 일시적으로 사용 불가능해진 타일입니다.
    ATTACK_OPPONENT = 4     # Red           : 상대방을 공격하는 칸입니다.

    HEAL_OPPONENT = 5       # Pink          : 상대방을 회복하는 칸입니다.

    @classmethod
    def from_value(cls, value: int) -> Optional[PanelItem]:
        """
        Get PanelItem Enum using value.
        :param value: value of the enum.
        :return: PanelItem Enum if value is valid. Else, `None` is returned.
        """
        return next(filter(
            lambda e: e.value == value,
            cls.__members__.values()
        ), None)

    @classmethod
    def items(cls) -> tuple[PanelItem, ...]:
        return cls.BLANK, cls.HEAL_SELF, cls.OPPONENT_BLOCK, cls.ATTACK_OPPONENT, cls.HEAL_OPPONENT

    @classmethod
    def itemWeights(cls) -> tuple[int, ...]:
        # BLANK : 50
        # HEAL_SELF : 15
        # OPPONENT_BLOCK : 5
        # ATTACK_OPPONENT : 20
        # HEAL_OPPONENT : 10
        return 50, 15, 5, 20, 10
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        setattr(self, '__handler__', lambda session, player, opponent: None)

    def set_handler(self, handler_func: ItemHandler):
        setattr(self, '__handler__', handler_func)

    def handle_item_event(self, session: 'GameSession', player: 'Player', opponent: 'Player'):
        return getattr(self, '__handler__')(session, player, opponent)

    def __int__(self):
        """
        Override how int(self) works.
        :return: value of this enum.
        """
        return self.value

    def __repr__(self) -> str:
        """
        Override how repr(self) works.
        :return: debug information of this enum.
        """
        return f'PanelItem.{self.name}({self.value})'

    def __str__(self) -> str:
        """
        Override how str(self) works.
        :return:
        """
        return f'PanelItem.{self.name}'


@PanelItem.HEAL_SELF.set_handler
def handleHealSelf(session: 'GameSession', player: 'Player', opponent: 'Player'):
    player.heal()


# @PanelItem.OPPONENT_BLOCK.set_handler
# def handleOpponentBlock(session: 'GameSession', player: 'Player', opponent: 'Player'):
#     # TODO : Write panel block logic. Maybe just sending empty map?
#     pass


@PanelItem.ATTACK_OPPONENT.set_handler
def handleAttackOpponent(session: 'GameSession', player: 'Player', opponent: 'Player'):
    opponent.damage()


@PanelItem.HEAL_OPPONENT.set_handler
def handleHealOpponent(session: 'GameSession', player: 'Player', opponent: 'Player'):
    opponent.heal()


"""
Player object
"""
# Constants
MAX_HP: Final[int] = 100          # Currently On Discussion.  # TODO : Fix value after the discussion.
MIN_HP: Final[int] = 0
ATTACK_DAMAGE: Final[int] = 10
HEAL_AMOUNT: Final[int] = 20     # Currently On Discussion.  # TODO : Fix value after the discussion.


class Player:
    """
    Player object which indicates player who plays the game.
    """

    client: WhackAMoleClient
    name: str
    session: GameSession

    # Game Data
    mapData: list[PanelItem]

    def __init__(
            self,
            client: WhackAMoleClient,
            session: GameSession
    ):
        """

        :param client: WhackAMoleClient object connected to this player.
        :param session: GameSession where player is registered.
        """
        self.client = client
        self.name = client.name
        self.session = session
        self.hp = MAX_HP

    @property
    def playerNumber(self) -> int:
        return self.client.clientNumber

    def notifyConnectionToPad(self):
        self.client.write_line(GameServerData.connectedNotification(self.playerNumber))

    @property
    def isDead(self) -> bool:
        return self.hp <= 0

    def heal(self):
        self.hp += HEAL_AMOUNT
        if self.hp > MAX_HP:
            # Fix player's health in health range (0 ~ MAX_HEALTH)
            self.hp = MAX_HP

    def damage(self):
        self.hp -= ATTACK_DAMAGE
        if self.hp < MIN_HP:
            self.session.on_player_death(self)

    def receiveData(self) -> GameClientData:
        return GameClientData.deserialize(self.client.read_line(), self)

    def sendData(self, mapData: list[PanelItem]):
        self.mapData = mapData
        self.client.write_line(GameServerData(list(map(lambda item: item.value, mapData))).serialize())


class GameFinishCode(enum.IntEnum):
    PLAYER_WIN = 0
    INVALID_PLAYER_COUNT = -1
    SHUTDOWN_COMMAND = -2


class GameInfo:
    __slots__ = ('finished', 'finish_code', 'players', 'map', 'winner', 'loser')
    finished: bool
    finish_code: Optional[GameFinishCode]
    players: dict[str, Player]
    map: dict[str, list[PanelItem]]
    winner: Optional[Player]
    loser: Optional[Player]

    @classmethod
    def initial(cls, players: list[Player]) -> GameInfo:
        instance = cls(players=dict(map(lambda p: (p.name, p), players)))
        instance.buildRandomMap()
        return instance

    def __init__(
            self,
            players: dict[str, Player],
    ):
        # Game Players
        self.players: dict[str, Player] = players

        # Game Map Data. Updated per round.
        self.map = None
        self.buildRandomMap()

        # Game Finish Data
        self.finished = False
        self.finish_code = None
        self.winner = None
        self.loser = None

    # Map Builders
    def buildRandomMap(self):
        map_data = dict(map(
            lambda playerName: (
                playerName,
                random.choices(PanelItem.items(), weights=PanelItem.itemWeights(), k=9)
            ),
            self.players.keys()
        ))
        self.map = map_data
        return map_data

    def set_winner(self, player: Player):
        if not isinstance(player, Player):
            raise TypeError(f'GameInfo.winner must be an instance of Player, not {type(player)}')
        self.winner = player

    def set_loser(self, player: Player):
        if not isinstance(player, Player):
            raise TypeError(f'GameInfo.loser must be an instance of Player, not {type(player)}')
        self.loser = player

    def finish_game(self, finish_code: GameFinishCode = GameFinishCode.PLAYER_WIN):
        self.finish_code = finish_code
        if self.finished:
            raise ValueError('GameInfo.finished is already True! (Game is already finished)')
        self.finished = True


class GameSession:
    """
    Game Session Object.
    """

    started_at: datetime.datetime
    players: list[Player]       # len(players) -- 2
    gameInfo: GameInfo
    __session_name__: str

    @classmethod
    def create(cls, gameManager=None) -> 'GameSession':
        startedAt = datetime.datetime.utcnow()
        startedAt.replace(tzinfo=datetime.timezone.utc)
        session = cls(startedAt, gameManager)
        if gameManager:
            gameManager.current_session = session

        return session

    def __init__(
            self,
            startedAt: datetime.datetime,
            game=None
    ):
        self.started_at = startedAt
        self.players = []
        self.gameInfo = None
        self.game = game  # Game Manager object.
        self.__game_thread__: Optional[threading.Thread] = None
        self.__session_name__: str = f'GameSession(start:{self.started_at})'

    def getPlayers(self):
        """
        @Deprecated
        Manually create player objects.
        :return:
        """
        self.game.logger.info('Setting up players')
        clients: list[WhackAMoleClient] = self.game.clients[:2]
        self.players = list(map(lambda c: Player(c, self), clients))
        self.gameInfo = GameInfo.initial(self.players)

    # Game run logic
    def _run(self):
        try:
            self.setup()
        except ImproperSessionPlayers as e:
            self.game.write_error_log(e)
            return
        while not self.gameInfo.finished:
            self.sendServerData()
            data = self.waitForClientData()
            self.handleData(data)
            self.draw()
        self.show_result()
        self.game.ui.handle_game_finish()
        self.close()
        if self.gameInfo.finish_code is GameFinishCode.SHUTDOWN_COMMAND:
            self.game.write_error_log('Command `Shutdown` Executed. Closed session.')

    # Game Runner
    def run(self):
        self.__game_thread__ = threading.Thread(target=self._run, name=self.__session_name__, daemon=True)
        self.__game_thread__.run()      # TODO : Solve blocking issue : Why my program gets blocked when using threading?

    @property
    def game_thread(self) -> Optional[threading.Thread]:
        """
        Get currently running game's thread. If game is not running, then thread will be None.
        :return: Optional[threading.Thread] object representing session's game thread.
        """
        return self.__game_thread__

    @property
    def is_running(self) -> bool:
        """
        Get if the session has running game thread. If game is not running, value will be True. Else, False.
        :return: bool value represents if game thread is running
        """
        return self.__game_thread__ is not None

    @property
    def is_game_running(self) -> bool:
        return self.is_running and not self.gameInfo.finished

    def shutdown(self):
        if self.is_running:
            self.gameInfo.finish_game(GameFinishCode.SHUTDOWN_COMMAND)

    # Game Phase
    def setup(self):
        self.getPlayers()
        if len(self.players) != 2:
            self.game.logger.info(msg='We have improper number of players. Cancel game startup.')
            raise ImproperSessionPlayers(self)
        self.game.display_game_screen()

    def sendServerData(self):
        print('Sending new map data to clients...')
        for playerName, mapData in self.gameInfo.buildRandomMap().items():
            self.gameInfo.players.get(playerName).sendData(mapData)
        print('ServerData sent.')

    def waitForClientData(self) -> list[GameClientData]:
        print('Waiting for client data...')
        data = list(map(
            lambda p: p.receiveData(),
            self.players
        ))
        print('ClientData received.')
        return data

    def handleData(self, clientData: list[GameClientData]):
        print('Handle client data...')
        for data in clientData:
            print(f'Handle client data of player {data.player.name}')
            if data.isHit:
                mapData = self.gameInfo.map[data.player.name]
                hitItem: PanelItem = mapData[data.hitIndex]
                # self.game.write_event_log(f'Player {data.player.name} hit panel {data.hitIndex} (item={hitItem.name})')
            else:
                hitItem = PanelItem.BLANK
                # self.game.write_event_log(f'Player {data.player.name} does not hit panel')

            p1, p2 = self.gameInfo.players.values()
            if p1.name == data.player.name:
                # player : p1, opponent : p2
                hitItem.handle_item_event(session=self, player=p1, opponent=p2)
            else:
                # player : p1, opponent : p2
                hitItem.handle_item_event(session=self, player=p2, opponent=p1)

    def draw(self):
        """
        Draw UI on screen.
        """
        # TODO : Implement UI.
        self.game.update_screen(self.gameInfo)

    def show_result(self):
        """
        Show the result of game.
        """
        self.game.show_result()

    def close(self):
        """
        Close the game session and upload data on raking (playtime, (Optional) score)
        """
        playtime = datetime.datetime.now(tz=self.started_at.tzinfo) - self.started_at

    # Event Handlers
    def on_player_death(self, player: Player):
        """
        Player Death Event Handler
        :param player: player instance who died.
        """
        # Since, currently the game has only two players, we can stop the game.
        self.players.pop(self.players.index(player))
        self.gameInfo.set_winner(self.players[0])
        self.gameInfo.set_loser(player)
        self.gameInfo.finish_game()
