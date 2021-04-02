from typing import NamedTuple, NoReturn

from bluetooth import *

#######################################################
# Scan
#######################################################


class DeviceStruct(NamedTuple):
    name: str
    port: int
    address = None

    def __str__(self) -> str:
        return f'Device<name={self.name},address={self.address},port={self.port}>'

    def assertValid(self) -> NoReturn:
        assert self.name is not None
        assert self.address is not None
        assert self.port is not None

    def isValid(self) -> bool:
        try:
            self.assertValid()
        except AssertionError:
            return False
        return True


deviceStruct = DeviceStruct('QCY-T5S', 1)


def scan():
    print(f'target device : {deviceStruct}')
    nearby_devices = discover_devices()
    print(f'bluetooth devices currently on nearby : {nearby_devices}')

    # scanning for target device
    for device_address in nearby_devices:
        print(lookup_name(device_address))
        if deviceStruct.name == lookup_name(device_address):
            deviceStruct.address = device_address
            break

    if deviceStruct.address is not None:
        print('device found. target address {}'.format(deviceStruct.address))
    else:
        print('could not find target bluetooth device nearby')

#######################################################
# Connect
#######################################################


def connect():
    # establishing a bluetooth connection
    try:
        sock = BluetoothSocket(RFCOMM)
        deviceStruct.assertValid()
        sock.connect((deviceStruct.address, deviceStruct.port))

        while True:
            try:
                recv_data = sock.recv(1024)
                print(recv_data)
                sock.send(recv_data)
            except KeyboardInterrupt:
                print("disconnected")
                sock.close()
                print("all done")
    except btcommon.BluetoothError as err:
        print('An error occurred : %s ' % err)


scan()
connect()
