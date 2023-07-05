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

    async def send(self, data, sync) -> None: ...

    async def recv(self, writer: Client) -> bytes: ...

    async def auth_client(self, sock: socket.socket) -> None: ...

    async def handle_client(self, sock: socket.socket) -> None: ...

    async def start(self) -> None: ...

