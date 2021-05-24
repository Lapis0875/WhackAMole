from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any


class Device(ABC):
    """
    Hardware device mock model.
    """
    name: str
    port: str
    address: Any

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def read(self) -> bytes:
        pass

    @abstractmethod
    def send(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def search(cls, name: str, port: Optional[int] = None) -> Device:
        pass

    def __init__(
            self,
            name: str,
            port: str,
            address: Any
    ):
        self.name = name
        self.port = port
        self.address = address


class WhackAMoleClient(Device):
    """
    Whack A Mole client device.
    Communicate using UART Serial.
    """
    def connect(self):
        pass

    def disconnect(self):
        pass

    def read(self) -> bytes:
        pass

    def send(self) -> bytes:
        pass

    def parse(self) -> :

    @classmethod
    def search(cls, name: str, port: Optional[int] = None) -> Device:
        pass