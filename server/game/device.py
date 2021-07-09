from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any, Final
import serial


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
            port: str
    ):
        self.name = name
        self.port = port


class WhackAMoleClient(Device):
    """
    Whack A Mole client device.
    Communicate using UART Serial.
    """

    # Constatns
    BAUDRATE: Final[int] = 9600

    def __init__(self, name: str, port: str, player):
        """

        Args:
            name (str) : name of the device.
            port (str) : port to connect.
            player (server.game.gameobjects.Player) : player instance which is connected to this device.
        """
        super(WhackAMoleClient, self).__init__(name, port)
        self.player = player
        self.serial: serial.Serial = serial.Serial(port, baudrate=self.BAUDRATE)

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
