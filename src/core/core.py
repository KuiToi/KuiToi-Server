# Developed by KuiToi Dev
# File core.core.py
# Written by: SantaSpeen
# Version 0.1.2
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import socket

from core import utils
from .tcp_server import TCPServer
from .udp_server import UDPServer


class Client:

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.log = utils.get_logger("client(id: )")
        self.addr = writer.get_extra_info("sockname")
        self.loop = asyncio.get_event_loop()
        self.cid = 0
        self.key = None
        self.nick = None
        self.roles = None
        self.guest = True
        self.alive = True

    def _update_logger(self):
        self.log = utils.get_logger(f"client(id:{self.cid})")

    def is_disconnected(self):
        if not self.alive:
            return True
        try:
            keep_alive = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
            if keep_alive:
                return False
        except OSError:
            pass
        self.alive = False
        return True

    def kick(self, reason):
        self.log.info(f"Client: \"IP: {self.addr!r}; ID: {self.cid}\" - kicked with reason: \"{reason}\"")
        self.tcp_send(b"K" + bytes(reason, "utf-8"))
        self.socket.close()
        self.alive = False

    def tcp_send(self, data):

        # TNetwork.cpp; Line: 383
        # BEAMP TCP protocol sends a header of 4 bytes, followed by the data.
        # [][][][][][]...[]
        # ^------^^---...-^
        # size    data

        data = data.replace(b" ", b"_")
        if len(data) == 10:
            data += b"."
        header = len(data).to_bytes(4, "little")
        self.log.debug(f'len(data) {len(data)}; header: {header}; send {header + data}')
        self.socket.send(header + data)


class Core:

    def __init__(self):
        self.log = utils.get_logger("core")
        self.clients = {}
        self.clients_counter = 0
        self.server_ip = config.Server["server_ip"]
        self.server_port = config.Server["server_port"]
        self.loop = asyncio.get_event_loop()
        self.tcp = TCPServer
        self.udp = UDPServer

    def get_client(self, sock=None, cid=None):
        if cid:
            return self.clients.get(cid)
        if sock:
            return self.clients.get(sock.getsockname())

    def create_client(self, *args, **kwargs):
        cl = Client(*args, **kwargs)
        self.clients_counter += 1
        cl.id = self.clients_counter
        self.clients.update({cl.id: cl})
        return cl

    async def check_alive(self):
        await asyncio.sleep(5)
        self.log.debug(f"Checking if clients is alive")
        for cl in self.clients.values():
            d = await cl.is_disconnected()
            if d:
                self.log.debug(f"Client ID: {cl.id} died...")

    async def main(self):
            self.tcp = self.tcp(self, self.server_ip, self.server_port)
            self.udp = self.udp(self, self.server_ip, self.server_port)
            self.log.info(i18n.ready)
        # while True:
            try:
                tasks = [console.start(), self.tcp.start(), self.udp.start()] # self.check_alive()
                await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            except Exception as e:
                await asyncio.sleep(1)
                print("Error: " + str(e))
                traceback.print_exc()
            except KeyboardInterrupt:
                raise KeyboardInterrupt

    def start(self):
        asyncio.run(self.main())

    def stop(self):
        self.log.info("Goodbye!")
        exit(0)
