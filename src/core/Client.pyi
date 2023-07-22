# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Core version: 0.4.1
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
from asyncio import StreamReader, StreamWriter, DatagramTransport
from logging import Logger
from typing import Tuple, List, Dict, Optional, Union

from core import Core, utils


class Client:

    def __init__(self, reader: StreamReader, writer: StreamWriter, core: Core) -> "Client":
        self._connect_time: float = 0.0
        self.__tasks = []
        self.__reader = reader
        self.__writer = writer
        self.__packets_queue = []
        self._udp_sock: Tuple[DatagramTransport | None, Tuple[str, int] | None] = (None, None)
        self._down_sock: Tuple[StreamReader | None, StreamWriter | None] = (None, None)
        self._log = utils.get_logger("client(id: )")
        self._addr: Tuple[str, int] = writer.get_extra_info("sockname")
        self._loop = asyncio.get_event_loop()
        self.__Core: Core = core
        self._cid: int = -1
        self._key: str = None
        self.nick: str = None
        self.roles: str = None
        self._guest = True
        self.__alive = True
        self._ready = False
        self._identifiers = []
        self._cars: List[Optional[Dict[str, int]]] = []
        self._snowman: Dict[str, Union[int, str]]  = {"id": -1, "packet": ""}
        self._last_position = {}
    async def __gracefully_kick(self): ...
    @property
    def _writer(self) -> StreamWriter: ...
    @property
    def log(self) -> Logger: ...
    @property
    def addr(self) -> Tuple[str, int]: ...
    @property
    def cid(self) -> int: ...
    def pid(self) -> int: ...
    @property
    def key(self) -> str: ...
    @property
    def guest(self) -> bool: ...
    @property
    def ready(self) -> bool: ...
    @property
    def identifiers(self) -> list: ...
    @property
    def cars(self) -> List[dict | None]: ...
    @property
    def last_position(self): ...
    def is_disconnected(self) -> bool: ...
    async def kick(self, reason: str) -> None: ...
    async def send_message(self, message: str | bytes, to_all: bool = True) -> None:...
    async def send_event(self, event_name: str, event_data: str) -> None: ...
    async def _send(self, data: bytes | str, to_all: bool = False, to_self: bool = True, to_udp: bool = False, writer: StreamWriter = None) -> None: ...
    async def _sync_resources(self) -> None: ...
    async def _recv(self, one=False) -> bytes | None: ...
    async def _split_load(self, start: int, end: int, d_sock: bool, filename: str, sl: float) -> None: ...
    async def _get_cid_vid(self, s: str) -> Tuple[int, int]: ...
    async def _spawn_car(self, data: str) -> None: ...
    async def _delete_car(self, raw_data: str = None, car_id : int =None) -> None: ...
    async def _edit_car(self, raw_data: str, data: str) -> None: ...
    async def _reset_car(self, raw_data: str) -> None: ...
    async def _handle_car_codes(self, data: str) -> None: ...
    async def _connected_handler(self) -> None: ...
    async def _chat_handler(self, data: str) -> None: ...
    async def _handle_codes(self, data: bytes) -> None: ...
    async def _looper(self) -> None: ...
    def _update_logger(self) -> None: ...
    async def _remove_me(self) -> None: ...
