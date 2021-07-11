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
    is_hit: bool
    hit_index: Optional[int]

    @classmethod
    def deserialize(cls, data: str) -> GameClientData:
        """
        Parse client->server data into Python object.

        Data is split using char ';'

        Data Format:
            "c;{is_hit};{hit_index}"

        Data Args:
            is_hit : bool
                boolean value which indicates whether any of tiles are hit.
            hit_index : int
                index of tile being hit.

        Args:
            data (str) : raw data to parse.
        Returns:
            GameClientData object.
        """
        string_params: list[str] = data.split(DATA_SPLIT_CHAR)[1:]     # ['c', '(is_hit)', '(hit_index)'] -> 0번째에 들어있는

        is_hit = eval(string_params[0])
        hit_index = int(string_params[1]) if string_params[1].isdigit() else None

        return cls(
            is_hit,
            hit_index
        )

    def __init__(
            self,
            is_hit: bool,
            hit_index: int
    ):
        self.is_hit: bool = is_hit
        self.hit_index: int = hit_index

    def serialize(self) -> str:
        return DATA_SPLIT_CHAR.join((self.prefix, self.is_hit, self.hit_index))


class GameServerData:
    """
    Represents data send to client (server -> client)

    Structure:
        s;(is_hit: boolean);(hit_index: integer[0~8])
    """

    # Class Constant
    prefix: Final[ClassVar[str]] = 's'

    map_data: list[list[int]]

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
        raw_map_string = data_args[0]
        map_data: list[list[int]] = []
        for i in range(0, 8, step=3):
            map_data.append([
                int(raw_map_string[i]),
                int(raw_map_string[i+1]),
                int(raw_map_string[i+2])
            ])

        return cls(
            map_data
        )

    def __init__(
            self,
            map_data: list[list[int]]
    ):
        self.map_data = map_data

    def serialize(self):
        # chain(iter[iter]) -> exhaust first iterable, then exhaust second iterable,
        # and keep going until the last iterable is exhausted.
        # chain(self.map_data) = [0, 1, 2] -> [3, 4, 5] -> [6, 7, 8]
        return self.prefix + DATA_SPLIT_CHAR + DATA_SPLIT_CHAR.join(map(str, chain(self.map_data)))

