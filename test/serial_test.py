from __future__ import annotations

from typing import List, Final
import serial

# Constants
LINE_SEP: Final[str] = '\n'
PARAM_SEP: Final[str] = ';'
BAUDRATE: Final[int] = 9600


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


def main():
    serial_port = serial.Serial("COM11", BAUDRATE)
    while True:
        data = receive(serial_port)
        print('Received.deserialize() >', data)
        print('-'*5)
        text = input('Line to send in serial. : ').strip().translate(str.maketrans('', '', '\r\n'))
        print('Your Input : ', text.encode('utf-8'))
        if text == 'exit':
            break
        print('-'*5)
        send(serial_port, SerialData.deserialize(data=text))
    serial_port.close()


if __name__ == '__main__':
    main()
