from __future__ import annotations

from typing import List, Optional, Dict, Final, Any
from itertools import chain
from server.type_hints import JSON

"""
Game Map Design
---------------
1. Map data.
Whack A Mole has 3*3 size of map. This map is flatten into 1-dimensional array, and accessed using integer index.
Each part of map is called 'tile' in below.

678
345     ->      [0,1,2,...,7,8]
012

2. 
"""


DATA_SPLIT_CHAR: Final[str] = ';'


def _serialize_data(*data) -> str:
    return DATA_SPLIT_CHAR.join(*data)


class GameClientData:
    @classmethod
    def deserialize(cls, data: str) -> GameClientData:
        """
        Parse client->server data into Python object.

        Data is split using char ';'

        Data Format:
            "{is_hit};{hit_index};{"

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
        raw_values: List[str] = data.split(DATA_SPLIT_CHAR)

        is_hit = bool(raw_values[0])
        hit_index = int(raw_values[1]) if raw_values[1].isdigit() else -1

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
        return _serialize_data(self.is_hit, self.hit_index)


class GameServerData:
    map_data: List[List[int]]

    @classmethod
    def deserialize(cls, data: str) -> GameServerData:
        """
        Parse raw server->client data into Python object.

        Data is split using char ';'

        Data Format:
            "s;{map_data};"

        Data args:
            map_Data: string (length : 9)
                index of tiles.
                format : 000000000
                example : 003001005


        Args:
            data (str) : raw data to parse.
        Returns:
            GameServerData object.
        """
        raw_values: List[str] = data.split(DATA_SPLIT_CHAR)

        # parse map_data
        map_data: List[List[int]] = []
        for i in range(3):
            map_data.append([
                int(raw_values[i]),
                int(raw_values[i+1]),
                int(raw_values[i+2])
            ])

        return cls(
            map_data
        )

    def __init__(
            self,
            map_data: List[List[int]]
    ):
        self.map_data = map_data

    def serialize(self):
        return _serialize_data(
            ''.join(map(str, chain(self.map_data)))
        )
