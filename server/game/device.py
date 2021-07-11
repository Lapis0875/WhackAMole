from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any, Final, ClassVar
import serial


class SerialDevice(ABC):
    """
    Hardware device mock model.
    """
    name: str
    port: str
    serialPort: serial.Serial

    def connect(self):
        self.serialPort.open()

    def disconnect(self):
        self.serialPort.close()

    @property
    def isConnected(self) -> bool:
        return self.serialPort.isOpen()

    def readline(self) -> str:
        buffer: str = ''
        if not self.serialPort.isOpen():
            self.serialPort.open()
        while self.serialPort.inWaiting():
            byte = self.serialPort.read(1)
            buffer += byte
            if byte == b'\n':
                return buffer

    def writeLine(self, line: str, encoding: str = 'utf-8'):
        byte_line = line.encode(encoding)
        self.serialPort.write(byte_line)

    @classmethod
    @abstractmethod
    def search(cls) -> list[SerialDevice]:  ...

    @classmethod
    @abstractmethod
    def search_for(cls, port: Optional[int] = None) -> SerialDevice: ...

    def __init__(
            self,
            name: str,
            port: str,
            baudrate: int = 9600
    ):
        self.name = name
        self.port = port
        self.serialPort = serial.Serial(port=port, baudrate=baudrate)


class WhackAMoleClient(SerialDevice):
    """
    Whack A Mole client device.
    Communicate using UART Serial.
    """
    BAUDRATE: Final[int] = 9600
    registeredClients: ClassVar[set] = set()

    def __init__(self, name: str, port: str):
        """

        Args:
            name (str) : name of the device.
            port (str) : port to connect.
            player (server.game.game_object.Player) : player instance which is connected to this device.
        """
        super(WhackAMoleClient, self).__init__(name, port, self.BAUDRATE)
        WhackAMoleClient.registeredClients.add(self)

    @classmethod
    def search(cls) -> list[WhackAMoleClient]:
        clients = []
        for i, port in enumerate(serial.tools.list_ports.comforts()):
            print(f'Found Serial Port : {port.name} ({port.device}))')
            print(f'Human Readable Description : {port.description}')
            print(f'Technical Description : {port.hwid}')
            print(f'USB Serial Number : {port.serial_number}')
            print(f'vid={port.vid}, pid={port.pid}')
            serialPort = serial.Serial(port=port.device, baudrate=cls.BAUDRATE)
            with serialPort:
                buffer: str = ''
                while serialPort.inWaiting():
                    byte = serialPort.read(1)
                    buffer += byte
                    if byte == b';':
                        serialPort.close()
                if buffer.startswith('c;'):
                    clients.append(cls(name=f'Player{i}', port=port.device))

        return clients

    @classmethod
    def search_for(cls, port: Optional[int] = None) -> WhackAMoleClient:
        matching_port = next(filter(lambda portInfo: portInfo.device == port, serial.tools.list_ports.comforts()), None)
        if matching_port:
            return cls(name=f'Player{len(WhackAMoleClient.registeredClients)}', port=matching_port.device)
