# Developed by KuiToi Dev
# File core.core.pyi
# Written by: SantaSpeen
# Version 0.2.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
from asyncio import StreamWriter, StreamReader
from threading import Thread
from typing import Callable, List, Dict, Tuple

from core import utils
from .tcp_server import TCPServer
from .udp_server import UDPServer


class Client:

    def __init__(self, reader: StreamReader, writer: StreamWriter, core: Core) -> "Client":
        self.reader = reader
        self.writer = writer
        self.down_rw: Tuple[StreamReader, StreamWriter] | Tuple[None, None] = (None, None)
        self.log = utils.get_logger("client(id: )")
        self.addr = writer.get_extra_info("sockname")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.cid = 0
        self.key: str = None
        self.nick: str = None
        self.roles: str = None
        self.guest = True
        self.alive = True
    def is_disconnected(self) -> bool: ...
    async def kick(self, reason: str) -> None: ...
    async def tcp_send(self, data: bytes) -> None: ...
    async def sync_resources(self) -> None: ...
    async def recv(self) -> bytes: ...
    async def looper(self) -> None: ...
    def _update_logger(self) -> None: ...


class Core:
    def __init__(self):
        self.log = utils.get_logger("core")
        self.loop = asyncio.get_event_loop()
        self.run = False
        self.direct = False
        self.clients: List[Client]= []
        self.clients_by_id: Dict[{int: Client}]= {}
        self.clients_by_nick: Dict[{str: Client}] = {}
        self.clients_counter: int = 0
        self.mods_dir: str = "mods"
        self.mods_list: list = []
        self.server_ip = config.Server["server_ip"]
        self.server_port = config.Server["server_port"]
        self.tcp = TCPServer
        self.udp = UDPServer
        self.web_thread: Thread = None
        self.web_stop: Callable = lambda: None
        self.client_major_version = "2.0"
        self.BeamMP_version = "3.2.0"
    def insert_client(self, client: Client) -> None: ...
    def create_client(self, *args, **kwargs) -> Client: ...
    async def check_alive(self) -> None: ...
    @staticmethod
    def start_web() -> None: ...
    @staticmethod
    def stop_me() -> None: ...
    async def authenticate(self, test=False) -> None: ...
    async def main(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
