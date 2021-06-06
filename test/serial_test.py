from __future__ import annotations

import time
from functools import partial
from typing import List, Final
import serial

# Constants
LINE_SEP: Final[str] = '\n'
PARAM_SEP: Final[str] = ';'
BAUDRATE: Final[int] = 9600


class SerialProgram:
    def __init__(self, serial_port: serial.Serial):
        self._serial: serial.Serial = serial_port
        self.__byte_listeners__: List = []
        self.__line_listeners__: List = []
        self._encoding: str = 'utf-8'
        self.__serial_input__ = None    # Callable function which receives serial.Serial object as a only parameter.

    @property
    def encoding(self) -> str:
        return self._encoding

    @encoding.setter
    def encoding(self, new_encoding):
        self._encoding = new_encoding

    def loop(self):
        while True:
            buffer: bytes = bytes()
            console_print(f'{self} > dispatching serial input handler :')
            self.__serial_input__(self._serial)

            console_print(f'{self} > dispatching serial bytes listeners :')
            while self._serial.in_waiting:
                single_byte: bytes = self._serial.read(1)
                # Call listeners which handles a single byte.
                for listener in self.__byte_listeners__:
                    listener(single_byte)
                buffer += single_byte
                if single_byte == serial.LF:
                    for listener in self.__line_listeners__:
                        listener(buffer.decode(self._encoding))
                    buffer = bytes()

    def byte_listener(self, func):
        console_print(f'{self} > registering function {func} as serial byte listener.')
        self.__byte_listeners__.append(func)
        return func

    def line_listener(self, func):
        console_print(f'{self} > registering function {func} as serial line listener.')
        self.__line_listeners__.append(func)

    def serial_input(self, func):
        console_print(f'{self} > registering function {func} as serial input handler.')
        self.__serial_input__ = func

    def __repr__(self):
        return f'SerialProgram(port -> {self._serial.port})'


class SerialData:
    @classmethod
    def deserialize(cls, data: str) -> SerialData:
        params: List[str] = data.split(PARAM_SEP)
        return cls(*params)

    def __init__(self, *args):
        self.args = args

    def __repr__(self) -> str:
        return f'SerialData(args={self.args})'

    def serialize(self) -> str:
        return PARAM_SEP.join(self.args)


def send(serial: serial.Serial, data: SerialData):
    """
    Send data serialized from SerialData object into serial.
    :param serial:  Serial object.
    :param data:    SerialData object to serialize.
    """
    print('Send : ', data.serialize())
    serial.write((data.serialize() + '\n').encode('utf-8'))


def receive(serial: serial.Serial) -> SerialData:
    """
    Receive data from serial and wrap into Python object.
    :param serial:  Serial object.
    :return:    SerialData object containing wrapped serial data.
    """
    line = serial.readline()
    print('Received : ', line)
    return SerialData.deserialize(data=line.strip().strip(b'\xba').decode('utf-8'))


CONSOLE_PREFIX: Final[str] = 'Console :'
console_print = partial(print, CONSOLE_PREFIX)


def main():
    # serial_port = serial.Serial("COM11", BAUDRATE)
    serial_port = serial.Serial("COM10", BAUDRATE)
    # serial_textIO_test(serial_port)
    text_send_test(serial_port)
    serial_port.close()


def serial_textIO_test(serial_port: serial.Serial):
    CLOSE_CMD = ('exit', 'quit', 'close', 'q')
    while True:
        data = receive(serial_port)
        console_print('Received.deserialize() >', data)
        console_print('-'*5)
        text = input('Line to send in serial. : ').strip().translate(str.maketrans('', '', '\r\n'))
        console_print('Your Input : ', text.encode('utf-8'))
        if text == 'exit':
            break
        console_print('-'*5)
        send(serial_port, SerialData.deserialize(data=text))


def text_send_test(serial_port: serial.Serial):
    ENCODING: Final[str] = 'utf-8'
    while True:
        text = input(f'{CONSOLE_PREFIX} : Write any text to send in serial. >')
        console_print(f'Your input > `{text}`')
        data = text.encode(ENCODING)
        console_print(f'UTF-8 encoded input > `{data}`')
        serial_port.writelines(data)
        line: bytes = serial_port.read_until()
        console_print(f'Read line from serial > {line}')
        console_print(f'Decode line data with UTF-8 > {line.decode(ENCODING)}')
        console_print('-'*5)


def serial_loop_test():
    serial_port = serial.Serial("COM10", BAUDRATE)
    serial_loop = SerialProgram(serial_port)

    @serial_loop.serial_input
    def serial_source(port: serial.Serial):
        port.write(b'bytes! yeah!')
        port.writelines(f'current system time : {time.time()}'.encode(serial_loop.encoding))
        port.flushInput()

    @serial_loop.byte_listener
    def byte_example(single_byte: bytes):
        console_print(byte_example.__name__, f'> I received a single byte! `{single_byte}`')

    @serial_loop.byte_listener
    def char_commands(single_byte: bytes):
        if single_byte == b'y':
            console_print(char_commands.__name__, f'> What do you mean yes, sir?')
        elif single_byte == b'n':
            console_print(char_commands.__name__, f'> What do you mean no, sir?')
        elif single_byte == b't':
            console_print(char_commands.__name__, f"> I'll bring you some teas, sir.")

    @serial_loop.line_listener
    def line_example(line: str):
        console_print(line_example.__name__, f'> I received a line! `{line}`')

    serial_loop.loop()


if __name__ == '__main__':
    # main()
    serial_loop_test()