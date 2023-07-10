# Developed by KuiToi Dev
# File core.core.py
# Written by: SantaSpeen
# Version 0.1.6
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import zlib

from core import utils
from .tcp_server import TCPServer
from .udp_server import UDPServer


class Client:

    def __init__(self, reader, writer, core):
        self.reader = reader
        self.writer = writer
        self.log = utils.get_logger("client(None:0)")
        self.addr = writer.get_extra_info("sockname")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.cid = 0
        self.key = None
        self.nick = None
        self.roles = None
        self.guest = True
        self.alive = True

    def _update_logger(self):
        self.log.debug(f"Update logger")
        self.log = utils.get_logger(f"client({self.nick}:{self.cid})")

    def is_disconnected(self):
        if not self.alive:
            return True
        res = self.writer.is_closing()
        if res:
            self.log.debug(f"Client Disconnected")
            self.alive = False
            return True
        else:
            self.log.debug(f"Client Alive")
            self.alive = True
            return False

    async def kick(self, reason):
        self.log.info(f"Client: \"IP: {self.addr!r}; ID: {self.cid}\" - kicked with reason: \"{reason}\"")
        await self.tcp_send(b"K" + bytes(reason, "utf-8"))
        # self.writer.close()
        # await self.writer.wait_closed()
        self.alive = False

    async def tcp_send(self, data):

        # TNetwork.cpp; Line: 383
        # BEAMP TCP protocol sends a header of 4 bytes, followed by the data.
        # [][][][][][]...[]
        # ^------^^---...-^
        #  size     data

        self.log.debug(f"tcp_send({data})")
        if len(data) == 10:
            data += b"."
        header = len(data).to_bytes(4, "little", signed=True)
        self.log.debug(f'len(data) {len(data)}; send {header + data}')
        self.writer.write(header + data)
        await self.writer.drain()

    async def recv(self):
        # if not self.is_disconnected():
        #     self.log.debug(f"Client with {self.nick}({self.cid}) disconnected")
        #     return b""
        header = await self.reader.read(4)  # header: 4 bytes

        int_header = 0
        for i in range(len(header)):
            int_header += header[i]

        if int_header <= 0:
            await self.kick("Invalid packet - header negative")
            return b""

        if int_header > 100 * MB:
            await self.kick("Header size limit exceeded")
            self.log.warn(f"Client {self.nick}({self.cid}) sent header of >100MB - "
                          f"assuming malicious intent and disconnecting the client.")
            return b""

        data = await self.reader.read(101 * MB)
        self.log.debug(f"header: `{header}`; int_header: `{int_header}`; data: `{data}`;")

        if len(data) != int_header:
            self.log.debug(f"WARN Expected to read {int_header} bytes, instead got {len(data)}")

        abg = b"ABG:"
        if len(data) > len(abg) and data.startswith(abg):
            data = zlib.decompress(data[len(abg):])
            self.log.debug(f"ABG: {data}")
            return data
        return data

    async def sync_resources(self):
        await self.tcp_send(b"P" + bytes(f"{self.cid}", "utf-8"))
        data = await self.recv()
        if data.startswith(b"SR"):
            await self.tcp_send(b"-")  # Cannot handle mods for now.
        data = await self.recv()
        if data == b"Done":
            await self.tcp_send(b"M/levels/" + bytes(config.Game['map'], 'utf-8') + b"/info.json")
        await self.last_handle()

    async def last_handle(self):
        # self.is_disconnected()
        self.log.debug(f"Alive: {self.alive}")
        while self.alive:
            data = await self.recv()
            if data == b"":
                if not self.alive:
                    break
                elif self.is_disconnected():
                    break
                else:
                    continue
            code = data.decode()[0]
            self.log.debug(f"Code: {code}, data: {data}")
            match code:
                case "H":
                    # Client connected
                    await self.tcp_send(b"Sn"+bytes(self.nick, "utf-8"))
                case "C":
                    # Chat
                    await self.tcp_send(data)


class Core:

    def __init__(self):
        self.log = utils.get_logger("core")
        self.loop = asyncio.get_event_loop()
        self.clients = {}
        self.clients_counter = 0
        self.server_ip = config.Server["server_ip"]
        self.server_port = config.Server["server_port"]
        self.tcp = TCPServer
        self.udp = UDPServer

    def get_client(self, sock=None, cid=None):
        if cid:
            return self.clients.get(cid)
        if sock:
            return self.clients.get(sock.getsockname())

    def insert_client(self, client):
        self.log.debug(f"Inserting client: {client.cid}")
        self.clients.update({client.cid: client, client.nick: client})

    def create_client(self, *args, **kwargs):
        client = Client(*args, **kwargs)
        self.clients_counter += 1
        client.id = self.clients_counter
        client._update_logger()
        self.log.debug(f"Create client: {client.cid}; clients_counter: {self.clients_counter}")
        return client

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
        tasks = [self.tcp.start(), self.udp.start(), console.start()]  # self.check_alive()
        t = asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        self.log.info(i18n.start)
        # TODO: Server auth
        ev.call_event("on_started")
        await t
        # while True:
        #     try:
        #         tasks = [console.start(), self.tcp.start(), self.udp.start()] # self.check_alive()
        #         await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        #     except Exception as e:
        #         await asyncio.sleep(1)
        #         print("Error: " + str(e))
        #         traceback.print_exc()
        #         break
        #     except KeyboardInterrupt:
        #         raise KeyboardInterrupt

    def start(self):
        asyncio.run(self.main())

    def stop(self):
        self.log.info(i18n.stop)
        exit(0)
