from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional, Any, NamedTuple
import bluetooth
from device import Device
from utils import createStandardLogger, Logger, DEBUG

JSON = Dict[str, Any]
logger: Logger = createStandardLogger('whackamole.models', DEBUG)


class JsonObject(ABC):
    @classmethod
    @abstractmethod
    def fromJson(cls) -> JSON:  ...

    @abstractmethod
    def toJson(self) -> JSON:   ...


class StudentInfo(NamedTuple):
    Grade: int
    Class: int
    Number: int


class GameSession:
    # Session Info
    id: int
    controllers: List[Controller]
    users: List[User]

    @classmethod
    def create(cls, controllers: List[Controller]) -> GameSession:
        return cls(controllers)

    def __init__(
            self,
            id: int,
            controllers: List[Controller]
    ):
        self.id = id
        self.controllers = controllers
        self.users = []

    def getSessionInfo(self) -> JSON:
        return {
            "id": self.id,
            "users_count": len(self.users),
            "controllers": [controller.getControllerInfo() for controller in self.controllers]
        }

    def joinUser(self, name: str, studentInfo: StudentInfo, controller: Controller) -> User:
        user = User(name, studentInfo, self, controller)
        self.users.append(user)
        return user

    async def run(self):
        while True:
            # TODO : Write Game Logic
            await asyncio.gather()


class User(JsonObject):
    name: str
    studentInfo: StudentInfo
    controller: Controller
    session: GameSession

    @classmethod
    def fromJson(cls) -> JSON:
        pass

    def __init__(self, name: str, studentInfo: StudentInfo, session: GameSession, controller: Controller) -> None:
        self.name = name
        self.studentInfo = studentInfo
        self.session = session
        self.controller = controller

    def toJson(self) -> JSON:
        return {
            "name": self.name,
            "student": {
                "grade": self.studentInfo.Grade,
                "class": self.studentInfo.Class,
                "number": self.studentInfo.Number
            },
            "session": self.session.getSessionInfo()
        }


class Controller(Device):
    # Device Info
    name: str
    port: int
    address: Any

    # Game Info
    user: Optional[User]
    session: Optional[GameSession]

    @classmethod
    def search(cls, name: str, port: Optional[int] = None) -> Controller:
        devices = bluetooth.discover_devices(duration=20)

        matching_devices = tuple(filter(lambda address: name == bluetooth.lookup_name(address), devices))
        logger.debug(matching_devices)

        return cls(name, port, matching_devices[0])

    def __init__(
            self,
            name: str,
            port: int,
            address: Any
    ):
        super().__init__(name, port, address)
        self.session: Optional[GameSession] = None

    @property
    def inSession(self) -> bool:
        return self.session is not None

    def joinSession(self, session: GameSession):
        self.session = session

    @property
    def hasUser(self) -> bool:
        return self.user is not None

    def setUser(self, user: User):
        self.user = user

    def getControllerInfo(self) -> JSON:
        return {
            "name": self.name,
            "port": self.port,
            "address": self.address
        }
