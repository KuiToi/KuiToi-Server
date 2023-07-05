# Developed by KuiToi Dev
# File core.udp_server.py
# Written by: SantaSpeen
# Version 0.0
# Licence: FPA
# (c) kuitoi.su 2023
from core import utils


class UDPServer:

    def __init__(self, core, host, port):
        self.log = utils.get_logger("UDPServer")
        self.Core = core
        self.host = host
        self.port = port

    async def start(self) -> None: ...

    async def stop(self) -> None: ...