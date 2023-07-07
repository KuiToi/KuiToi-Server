# Developed by KuiToi Dev
# File core.tcp_server.pyi
# Written by: SantaSpeen
# Version 0.1.2
# Licence: FPA
# (c) kuitoi.su 2023
from asyncio import StreamWriter, StreamReader
import socket

from core import utils, Core
from core.core import Client


class TCPServer:
    def __init__(self, core: Core, host, port):
        self.log = utils.get_logger("TCPServer")
        self.Core = core
        self.host = host
        self.port = port
    async def recv(self, client: Client) -> bytes: ...
    async def auth_client(self, sock: socket.socket) -> None: ...
    async def handle_download(self, sock: socket.socket) -> None: ...
    async def handle_code(self, code: str, sock: socket.socket) -> None: ...
    async def handle_client(self, sock: socket.socket) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...

