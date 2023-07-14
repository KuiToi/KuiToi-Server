import asyncio
from asyncio import StreamReader, StreamWriter
from typing import Tuple

from core import Core, utils


class Client:

    def __init__(self, reader: StreamReader, writer: StreamWriter, core: Core) -> "Client":
        self.reader = reader
        self.writer = writer
        self.down_rw: Tuple[StreamReader, StreamWriter] | Tuple[None, None] = (None, None)
        self.log = utils.get_logger("client(id: )")
        self.addr = writer.get_extra_info("sockname")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.cid: int = -1
        self.key: str = None
        self.nick: str = None
        self.roles: str = None
        self.guest = True
        self.alive = True
        self.ready = False
    def is_disconnected(self) -> bool: ...
    async def kick(self, reason: str) -> None: ...
    async def tcp_send(self, data: bytes, to_all:bool = False, writer: StreamWriter = None) -> None: ...
    async def sync_resources(self) -> None: ...
    async def recv(self) -> bytes: ...
    async def _split_load(self, start: int, end: int, d_sock: bool, filename: str) -> None: ...
    async def looper(self) -> None: ...
    def _update_logger(self) -> None: ...
    async def remove_me(self) -> None: ...
