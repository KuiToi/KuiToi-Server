# Developed by KuiToi Dev
# File core.tcp_server.pyi
# Written by: SantaSpeen
# Version 0.2.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
from asyncio import StreamWriter, StreamReader
from typing import Tuple

from core import utils, Core
from core.core import Client


class TCPServer:
    def __init__(self, core: Core, host, port):
        self.log = utils.get_logger("TCPServer")
        self.Core = core
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()
    async def auth_client(self, reader: StreamReader, writer: StreamWriter) -> Tuple[bool, Client]: ...
    async def handle_download(self, writer: StreamWriter) -> bool: ...
    async def handle_code(self, code: str, reader: StreamReader, writer: StreamWriter) -> bool: ...
    async def handle_client(self, reader: StreamReader, writer: StreamWriter) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...

