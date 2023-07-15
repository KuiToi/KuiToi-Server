import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Tuple

from core import Core, utils


class Client:

    def __init__(self, reader: StreamReader, writer: StreamWriter, core: Core) -> "Client":
        self.__reader = reader
        self.__writer = writer
        self._down_rw: Tuple[StreamReader, StreamWriter] | Tuple[None, None] = (None, None)
        self._log = utils.get_logger("client(id: )")
        self._addr = writer.get_extra_info("sockname")
        self._loop = asyncio.get_event_loop()
        self.__Core = core
        self._cid: int = -1
        self._key: str = None
        self._nick: str = None
        self._roles: str = None
        self._guest = True
        self.__alive = True
        self._ready = False
    @property
    def log(self):
        return self._log
    @property
    def addr(self):
        return self._addr
    @property
    def cid(self):
        return self._cid
    @property
    def key(self):
        return self._key
    @property
    def nick(self):
        return self._nick
    @property
    def roles(self):
        return self._roles
    @property
    def guest(self):
        return self._guest
    @property
    def ready(self):
        return self._ready
    def is_disconnected(self) -> bool: ...
    async def kick(self, reason: str) -> None: ...
    async def _tcp_send(self, data: bytes, to_all:bool = False, writer: StreamWriter = None) -> None: ...
    async def _sync_resources(self) -> None: ...
    async def _recv(self) -> bytes: ...
    async def _split_load(self, start: int, end: int, d_sock: bool, filename: str) -> None: ...
    async def _looper(self) -> None: ...
    def _update_logger(self) -> None: ...
    async def _remove_me(self) -> None: ...
