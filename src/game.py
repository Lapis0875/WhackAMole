from __future__ import annotations

from typing import List

from src.models import GameSession, User, Controller


"""
Game Map Design
---------------
1. Map data.
Whack A Mole has 3*3 size of map. This map is flatten into 1-dimensional array, and accessed using integer index.
Each part of map is called 'tile' in below.

678
345     ->      [0,1,2,...,7,8]
012


"""


class GameClientData:
    @classmethod
    def from_data(cls, data: str) -> GameClientData:
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
        parsed = cls.parse(data)

    @classmethod
    def parse(cls, data: str) -> List[str]:
        return data.split(';')


class GameServerData:
    @classmethod
    def from_data(cls, data: str) -> GameServerData:
        """
        Parse raw server->client data into Python object.

        Data is split using char ';'
        Data order : [map_data: list[int], ]

        Data Format:
            "{targets};"

        Data args:
            targets: list[int]
                index of tiles.

                678
                345 -> 012345678
                012


        Args:
            data (str) : raw data to parse.
        Returns:
            GameServerData object.
        """
        parsed = cls.parse(data)
        return cls(
            parsed[0]
        )

    @classmethod
    def parse(cls, data: str) -> List[str]:
        return data.split(';')

    def __init__(
            self,
            targets: List[int]
    ):
