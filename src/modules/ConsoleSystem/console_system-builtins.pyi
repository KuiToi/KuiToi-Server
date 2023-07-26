from logging import Logger
from typing import AnyStr

from core import get_logger


class RCONSystem:
    console = None

    def __init__(self, key, host, port):
        self.log = get_logger("RCON")
        self.key = key
        self.host = host
        self.port = port

    async def start(self): ...
    async def stop(self): ...

class console:
    rcon: RCONSystem = RCONSystem

    @staticmethod
    def alias() -> dict: ...
    @staticmethod
    def add_command(key: str, func, man: str = None, desc: str = None, custom_completer: dict = None) -> dict: ...
    @staticmethod
    async def start() -> None: ...
    @staticmethod
    def builtins_hook() -> None: ...
    @staticmethod
    def logger_hook() -> None: ...
    @staticmethod
    def log(s: str) -> None: ...
    @staticmethod
    def write(s: str) -> None: ...
    @staticmethod
    def __lshift__(s: AnyStr) -> None: ...
