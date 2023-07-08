# Developed by KuiToi Dev
# File core.core.pyi
# Written by: SantaSpeen
# Version 0.1.2
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import socket
from asyncio import StreamWriter, AbstractEventLoop, StreamReader
from asyncio.trsock import TransportSocket

from core import utils
from .tcp_server import TCPServer
from .udp_server import UDPServer
class Client:

    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer
        self.log = utils.get_logger("client(id: )")
        self.addr = writer.get_extra_info("sockname")
        self.loop = asyncio.get_event_loop()
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
    async def last_handle(self) -> bytes: ...


class Core:
    def __init__(self):
        self.clients_counter: int = 0
        self.log = utils.get_logger("core")
        self.clients = dict()
        self.server_ip = config.Server["server_ip"]
        self.server_port = config.Server["server_port"]
        self.loop = asyncio.get_event_loop()
        self.tcp = TCPServer
        self.udp = UDPServer
    def insert_client(self, client: Client) -> None: ...
    def create_client(self, *args, **kwargs) -> Client: ...
    async def check_alive(self) -> None: ...
    async def main(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

