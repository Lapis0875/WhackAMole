from __future__ import annotations

import enum
from typing import Optional


class PanelItem(enum.IntEnum):
    """
    Game Item Enum :
    this enum represents items which are displayed on mole (Panel which player hits).
    """
    # 0~4 : Positive items (for player self)
    BLANK = 0               # Transparent   : 아무런 아이템도 없는 빈 칸입니다.
    HEAL_SELF = 1           # Green         : 자신을 회복하는 칸입니다.
    OPPONENT_BLOCK = 2      # Purple        : 상대방이 일시적으로 자신을 공격하지 못하게 합니다.
    ATTACK_OPPONENT = 3     # Red           : 상대방을 공격하는 칸입니다.

    # 5~9 : Negative items (for player self)
    HEAL_OPPONENT = 5       # Pink          : 상대방을 회복하는 칸입니다.

    @classmethod
    def parse(cls, value: int) -> Optional[PanelItem]:
        return next(filter(
            lambda e: e.value == value,
            cls.__members__.values()
        ), None)


class Player:
    """
    Player object which indicates player who plays the game.
    """
    pass