# Developed by KuiToi Dev
# File core.udp_server.py
# Written by: SantaSpeen
# Core version: 0.3.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
from typing import Tuple

from core import utils


class UDPServer:

    def __init__(self, core, host=None, port=None):
        self.log = utils.get_logger("UDPServer")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.host = host
        self.port = port
        self.run = False
        self.transport = None
    def connection_made(self, transport: asyncio.DatagramTransport): ...
    def datagram_received(self, data: bytes, addr: Tuple[str, int]): ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...