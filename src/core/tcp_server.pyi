# Developed by KuiToi Dev
# File core.tcp_server.pyi
# Written by: SantaSpeen
# Core version: 0.4.5
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
from asyncio import StreamWriter, StreamReader
from typing import Tuple

from core import utils, Core
from core.Client import Client


class TCPServer:
    def __init__(self, core: Core, host, port):
        self.log = utils.get_logger("TCPServer")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.host = host
        self.port = port
        self.run = False
    async def auth_client(self, reader: StreamReader, writer: StreamWriter) -> Tuple[bool, Client]: ...
    async def set_down_rw(self, reader: StreamReader, writer: StreamWriter) -> bool: ...
    async def handle_code(self, code: str, reader: StreamReader, writer: StreamWriter) -> Tuple[bool, Client]: ...
    async def handle_client(self, reader: StreamReader, writer: StreamWriter) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...

