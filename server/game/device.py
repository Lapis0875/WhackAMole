from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import suppress
from random import randint
from typing import Optional, Any, Final, ClassVar
import serial
from serial.tools.list_ports import comports

from timeout import TimeoutContext, ContextTimeoutError


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

    def read_line(self) -> str:
        buffer: str = ''
        if not self.serialPort.isOpen():
            self.serialPort.open()
        while self.serialPort.inWaiting():
            byte = self.serialPort.read(1)
            buffer += byte
            if byte == b'\n':
                return buffer

    def write_line(self, line: str, encoding: str = 'utf-8'):
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

    def __init__(self, name: str, port: str, clientNumber: int):
        """

        Args:
            name (str) : name of the device.
            port (str) : port to connect.
            player (server.game.game_object.Player) : player instance which is connected to this device.
        """
        super(WhackAMoleClient, self).__init__(name, port, self.BAUDRATE)
        self.clientNumber: int = clientNumber
        WhackAMoleClient.registeredClients.add(self)

    @classmethod
    def search(cls) -> list[WhackAMoleClient]:
        clients = []
        print('Found Serial ports :')
        print(list(map(lambda p: p.name, comports(include_links=True))))
        for i, port in enumerate(comports(include_links=True)):
            # DEBUG
            print(f'Found Serial Port : {port.name} ({port.device}))')
            print(f'│ Human Readable Description : {port.description}')
            # print(f'Technical Description : {port.hwid}')
            # print(f'USB Serial Number : {port.serial_number}')
            print(f'│ vid={port.vid}, pid={port.pid}')
            try:
                serialPort = serial.Serial(port=port.device, baudrate=cls.BAUDRATE, timeout=5)
                # serialPort.open()
                print('├ Try read 2 bytes')
                resp = serialPort.read(2)
                print(f'├ resp = {resp}')
                if resp.startswith(b'c;'):
                    print(f'└ Found WhackAMole Client device! Registering...')
                    clients.append(cls(name=f'Player{i}', port=port.device, clientNumber=i))
                serialPort.close()
            except serial.serialutil.SerialException:
                print(f'└ Cannot open serial port {port.name} ({port.device}). Skipping...')
        print('Finish wrapping clients.')
        return clients

    @classmethod
    def search_for(cls, port: Optional[int] = None) -> WhackAMoleClient:
        matching_port = next(filter(lambda portInfo: portInfo.device == port, comports()), None)
        if matching_port:
            return cls(name=f'Player{len(WhackAMoleClient.registeredClients)}', port=matching_port.device)


# Objects for Feature Test

class FakeWAMClient:
    """
    Fake WhackAMoleClient object, which sends response without attached to physical client (arduino)
    """
    def __init__(self, name: str, port: str, clientNumber: int):
        self.name = name
        self.port = port
        self.clientNumber = clientNumber
        # No serial.Serial object.
        self.last_server_data: str = None

    def send_no_hit_response(self):
        return f'c;False'

    def send_hit_response(self):
        return f'c;True;{randint(0, 8)}'

    def read_line(self) -> str:
        flag = randint(0, 1)
        if flag:
            return self.send_hit_response()
        else:
            return self.send_no_hit_response()

    def write_line(self, line: str, encoding: str = 'utf-8'):
        self.last_server_data = line



