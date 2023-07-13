# Developed by KuiToi Dev
# File core.udp_server.py
# Written by: SantaSpeen
# Version 0.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio

from core import utils


class UDPServer:

    def __init__(self, core, host, port):
        self.log = utils.get_logger("UDPServer")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.host = host
        self.port = port
        self.run = False
    async def handle_client(self, srv_sock) -> None: ...
    async def start(self) -> None: ...

    async def stop(self) -> None: ...