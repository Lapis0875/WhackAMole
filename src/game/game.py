from __future__ import annotations

from typing import List, Optional, Dict, Final, Any

from . import parse
from src.type_hints import JSON

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
        parsed: JSON = cls.parse(data)
        return cls(**parsed)

    @classmethod
    def parse(cls, data: str) -> JSON:
        data_raw: List[str] = data.split(DATA_SPLIT_CHAR)
        data: JSON = {
            'is_hit': bool(data_raw[0]),
            'hit_index': int(data_raw[1]) if data_raw[1].isdigit() else None
        }
        return data

    def __init__(
            self,
            is_hit: bool,
            hit_index: Optional[int]
    ):
        self.is_hit: bool = is_hit
        self.hit_index: Optional[int] = hit_index

    def serialize(self) -> str:
        return _serialize_data(self.is_hit, self.hit_index)


class GameServerData:
    targets: List[int]

    @classmethod
    def deserialize(cls, data: str) -> GameServerData:
        """
        Parse raw server->client data into Python object.

        Data is split using char ';'

        Data Format:
            "{targets};"

        Data args:
            targets: list[int]
                index of tiles.
                format : [index(, ...)]
                example : [0, 1, 6]


        Args:
            data (str) : raw data to parse.
        Returns:
            GameServerData object.
        """
        parsed = cls.parse(data)
        return cls(**parsed)

    @classmethod
    def parse(cls, data: str) -> JSON:
        data_raw: List[str] = data.split(DATA_SPLIT_CHAR)
        data: JSON = {
            'targets': parse.parse_list_expr(data_raw[0])
        }
        return data

    def __init__(
            self,
            targets: List[int]
    ):
        self.targets = targets

    def serialize(self):
        return _serialize_data(self.targets)
