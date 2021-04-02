from __future__ import annotations
from typing import Optional, Any


class Device:
    """
    Hardware device mock model.
    """

    def connect(self):
        pass

    def disconnect(self):
        pass

    def read(self) -> bytes:
        pass

    def send(self) -> bytes:
        pass

    @classmethod
    def search(cls, name: str, port: Optional[int] = None) -> Device:
        pass

    def __init__(
            self,
            name: str,
            port: int,
            address: Any
    ):
        pass
