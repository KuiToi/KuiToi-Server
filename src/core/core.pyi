# Developed by KuiToi Dev
# File core.core.pyi
# Written by: SantaSpeen
# Version 0.1.2
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
from asyncio import StreamWriter, AbstractEventLoop, StreamReader
from asyncio.trsock import TransportSocket

from core import utils
from .tcp_server import TCPServer
from .udp_server import UDPServer
class Client:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.cid: int = 0
        self.nick: str = None
        self.log = utils.get_logger("client")
        self.writer: StreamWriter = writer
        self.reader: StreamReader = reader
        self.addr: tuple = writer.get_extra_info('peername')
        self.socket: TransportSocket = writer.get_extra_info('socket')
        self.loop: AbstractEventLoop = asyncio.get_event_loop()
        self.alive = True
    def is_disconnected(self) -> bool: ...
    def kick(self, reason: str) -> None: ...
    def tcp_send(self, data: bytes) -> None: ...


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
    def create_client(self, *args, **kwargs) -> Client: ...
    async def check_alive(self) -> None: ...
    async def main(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

