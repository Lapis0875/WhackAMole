from __future__ import annotations

from typing import List, Optional, Dict, Final, Any, ClassVar
from itertools import chain


DATA_SPLIT_CHAR: Final[str] = ';'

_serialize_data = lambda *data: DATA_SPLIT_CHAR.join(data)


class GameClientData:
    """
    Represents data sent from client (client -> server)

    Structure:
        c;(is_hit: boolean);(hit_index: integer[0~8])
    """

    # Class Constant
    prefix: Final[ClassVar[str]] = 'c'

    # Instance attribute
    isHit: bool
    hitIndex: Optional[int]

    @classmethod
    def deserialize(cls, data: str, player=None) -> GameClientData:
        """
        Parse client->server data into Python object.

        Data is split using char ';'

        Data Format:
            "c;{is_hit};{hit_index}"

        Data Args:
            is_hit : bool
                boolean value which indicates whether any of tiles are hit.
            hit_index : Optional[int]
                index of tile being hit.

        Args:
            data (str) : raw data to parse.
        Returns:
            GameClientData object.
        """
        string_params: list[str] = data.split(DATA_SPLIT_CHAR)[1:]     # ['c', '(is_hit)', '(hit_index)'] -> 0번째에 들어있는

        is_hit = eval(string_params[0])
        hit_index = int(string_params[1]) if len(string_params) == 2 and string_params[1].isdigit() else None

        return cls(
            is_hit,
            hit_index,
            player=player
        )

    def __init__(
            self,
            isHit: bool,
            hitIndex: int,
            player=None
    ):
        self.player = player
        self.isHit: bool = isHit
        self.hitIndex: int = hitIndex

    def serialize(self) -> str:
        return DATA_SPLIT_CHAR.join((self.prefix, self.isHit, self.hitIndex))


class GameServerData:
    """
    Represents data send to client (server -> client)

    Structure:
        s;(is_hit: boolean);(hit_index: integer[0~8])
    """

    # Class Constant
    prefix: Final[ClassVar[str]] = 's'

    mapData: list[int]

    @classmethod
    def deserialize(cls, data: str) -> GameServerData:
        """
        Parse raw server->client data into Python object.

        Data is split using char ';'

        Data Format:
            "s;{map_data}"

        Data args:
            map_data: string (length : 9)
                Item info of each tile.
                Item info is described using item's unique number.

                format : 000000000
                example : 003001005


        Args:
            data (str) : raw data to parse.
        Returns:
            GameServerData object.
        """
        data_args: list[str] = data.split(DATA_SPLIT_CHAR)[1:]     # ['s', '(map_data)'] -> ignore server data prefix(s) in index 0.

        # parse map_data
        rawMapStr = data_args[0]
        mapData: list[int] = list(map(int, rawMapStr))

        return cls(mapData)

    def __init__(
            self,
            mapData: list[int]
    ):
        self.mapData = mapData

    def serialize(self):
        # chain(iter[iter]) -> exhaust first iterable, then exhaust second iterable,
        # and keep going until the last iterable is exhausted.
        # chain(self.map_data) = [0, 1, 2] -> [3, 4, 5] -> [6, 7, 8]
        return self.prefix + DATA_SPLIT_CHAR + DATA_SPLIT_CHAR.join(map(str, self.mapData))

    # Presets
    @classmethod
    def connectedNotification(cls, player_num: int):
        return cls(mapData=[player_num]*9)  # Blink client's pad with color based on player number


