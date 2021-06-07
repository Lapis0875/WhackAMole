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
    class ServerData:
        prefix: Final[str] = 's;'

        def __init__(self, text: str, encoding: str):
            self.text = text
            self.encoding = encoding

        def serialize(self):
            return (self.prefix + self.text).encode(self.encoding)

        def __repr__(self):
            return f'ServerData({self.text}).encode({self.encoding})'

    class ClientData:
        prefix: Final[bytes] = b'c;'

        @classmethod
        def validate(cls, data: bytes):
            return data.startswith(cls.prefix)

        @classmethod
        def deserialize(cls, data: bytes) -> SerialProgram.ClientData:
            return cls(data)

        def __init__(self, data: bytes):
            self.data = data.strip(self.prefix)

        def serialize(self) -> bytes:
            return self.prefix + self.data

        def force_encode(self, encoding: str) -> str:
            try:
                return self.data.decode(encoding)
            except UnicodeDecodeError:
                return self.data.replace(b'\xff', b'?').decode(encoding)

        def __repr__(self):
            return f'ClientData({self.data})'

    def __init__(self, serial_port: serial.Serial):
        self._serial: serial.Serial = serial_port
        self._encoding: str = 'utf-8'
        self._close_flag: bool = False

        # listeners/handlers
        self.__byte_listeners__: List = []
        self.__line_listeners__: List = []
        self.__data_listeners__: List = []
        self.__serial_input__ = None    # Callable function which receives serial.Serial object as a only parameter.

    @property
    def serial(self) -> serial.Serial:
        return self._serial

    @property
    def port(self) -> str:
        return self._serial.port

    @property
    def baudrate(self) -> int:
        return self._serial.baudrate

    @property
    def encoding(self) -> str:
        return self._encoding

    @encoding.setter
    def encoding(self, new_encoding):
        self._encoding = new_encoding

    def wrap_server_data(self, text: str) -> SerialProgram.ServerData:
        return SerialProgram.ServerData(text, self.encoding)

    def wrap_client_data(self, data: bytes) -> SerialProgram.ClientData:
        return SerialProgram.ClientData.deserialize(data)

    def schedule_close(self):
        console_print(f'{self} > scheduling loop close.')
        self._close_flag = True

    def loop(self):
        console_print(f'{self} > starting loop...')
        if not self._serial.is_open:
            console_print(f'{self} > serial port is not open. try opening it...')
            self._serial.open()
            console_print(f'{self} > opened serial port.')
        else:
            console_print(f'{self} > serial port is already open.')
        while True:
            if self._close_flag:
                break
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
                        listener(buffer)
                    if buffer.startswith(SerialProgram.ClientData.prefix):
                        for listener in self.__data_listeners__:
                            listener(self.wrap_client_data(buffer))
                    buffer = bytes()

        # Close loop
        console_print(f'{self} > closing loop.')
        self._serial.close()
        console_print(f'{self} > closed serial loop.')

    def write(self, data: SerialProgram.ServerData):
        self._serial.write(data.serialize())

    def byte_listener(self, func):
        """
        register listener which listens every single byte on serial.
        :param func: function to register as byte-listener.
        :return: original function.
        """
        console_print(f'{self} > registering function {func} as serial byte listener.')
        self.__byte_listeners__.append(func)
        return func

    def line_listener(self, func):
        """
        register listener which listens single line data (bytes data which ends with \n).
        :param func: function to register as line-listener.
        :return: original function.
        """
        console_print(f'{self} > registering function {func} as serial line listener.')
        self.__line_listeners__.append(func)

    def data_listener(self, func):
        """
        register listener which listens wrapped python object containing single line data.
        :param func: function to register as line-listener.
        :return: original function.
        """
        console_print(f'{self} > registering function {func} as serial data listener.')
        self.__data_listeners__.append(func)

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


CONSOLE_PREFIX: Final[str] = 'Console'
console_print = partial(print, CONSOLE_PREFIX + ' :')


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
    serial_port = serial.Serial("COM12", BAUDRATE)
    serial_loop = SerialProgram(serial_port)

    @serial_loop.serial_input
    def serial_source(port: serial.Serial):
        text: str = input(f'{CONSOLE_PREFIX} : Write any text to send in serial >')
        if not text.endswith(LINE_SEP):
            text += LINE_SEP
        data: SerialProgram.ServerData = serial_loop.wrap_server_data(text)
        console_print(f'Your input (utf-8 encoded) > {data.serialize()}')
        serial_loop.write(data)

    # @serial_loop.byte_listener
    # def byte_example(single_byte: bytes):
    #     console_print(byte_example.__name__, f'> I received a single byte! `{single_byte}`')
    #
    # @serial_loop.byte_listener
    # def char_commands(single_byte: bytes):
    #     if single_byte == b'y':
    #         console_print(char_commands.__name__, f'> What do you mean yes, sir?')
    #     elif single_byte == b'n':
    #         console_print(char_commands.__name__, f'> What do you mean no, sir?')
    #     elif single_byte == b't':
    #         console_print(char_commands.__name__, f"> I'll bring you some teas, sir.")
    #     elif single_byte == b'q':
    #         serial_loop.schedule_close()

    @serial_loop.line_listener
    def line_example(line: bytes):
        print(f'Serial({serial_loop.port}) > {line}')

    @serial_loop.data_listener
    def data_example(data: SerialProgram.ClientData):
        console_print(f'{serial_loop} > data > `{data.serialize()}`')
        console_print(f'{serial_loop} > data > try force encode : {data.force_encode(serial_loop.encoding)}')

    serial_loop.loop()


if __name__ == '__main__':
    # main()
    serial_loop_test()
