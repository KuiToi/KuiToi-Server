# Developed by KuiToi Dev
# File core.core.py
# Written by: SantaSpeen
# Version 0.1.6
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import os
import time
import traceback
import zlib
from threading import Thread

import aiohttp
import uvicorn

from core import utils
from core.tcp_server import TCPServer
from core.udp_server import UDPServer
from modules.WebAPISystem import app as webapp


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
                    await self.tcp_send(b"Sn" + bytes(self.nick, "utf-8"))
                case "C":
                    # Chat
                    await self.tcp_send(data)


class Core:

    def __init__(self):
        self.log = utils.get_logger("core")
        self.loop = asyncio.get_event_loop()
        self.run = False
        self.direct = False
        self.clients = {}
        self.clients_counter = 0
        self.mods_dir = "./mods"
        self.mods_list = [0, ]
        self.server_ip = config.Server["server_ip"]
        self.server_port = config.Server["server_port"]
        self.tcp = TCPServer
        self.udp = UDPServer
        self.web_thread = None
        self.web_pool = webapp.data_pool
        self.web_stop = None

        self.client_major_version = "2.0"
        self.BEAMP_version = "3.2.0"

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

    @staticmethod
    def start_web():
        global uvserver
        uvconfig = uvicorn.Config("modules.WebAPISystem.app:web_app",
                                  host=config.WebAPI["server_ip"],
                                  port=config.WebAPI["server_port"],
                                  loop="asyncio")
        uvserver = uvicorn.Server(uvconfig)
        webapp.uvserver = uvserver
        uvserver.run()

    @staticmethod
    async def stop_me():
        while webapp.data_run[0]:
            await asyncio.sleep(1)
        raise KeyboardInterrupt

    # noinspection SpellCheckingInspection,PyPep8Naming
    async def authenticate(self, test=False):
        if config.Auth["private"] or self.direct:
            if test:
                self.log.info(f"Server runnig in Direct connect mode.")
            self.direct = True
            return

        BEAM_backend = ["backend.beammp.com", "backup1.beammp.com", "backup2.beammp.com"]
        modlist = ""
        for mod in self.mods_list:
            if type(mod) == int:
                continue
            modlist += f"/{os.path.basename(mod['path'])};"
        modstotalsize = self.mods_list[0]
        modstotal = len(self.mods_list) - 1
        while self.run:
            data = {"uuid": config.Auth["key"], "players": len(self.clients), "maxplayers": config.Game["players"],
                    "port": config.Server["server_port"], "map": f"/levels/{config.Game['map']}/info.json",
                    "private": config.Auth['private'], "version": self.BEAMP_version, "clientversion": self.client_major_version,
                    "name": config.Server["name"], "modlist": modlist, "modstotalsize": modstotalsize,
                    "modstotal": modstotal, "playerslist": "", "desc": config.Server['description'], "pass": False}
            self.log.debug(f"Auth: data {data}")

            # Sentry?
            ok = False
            body = {}
            code = 0
            for server_url in BEAM_backend:
                url = "https://" + server_url + "/heartbeat"
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, data=data, headers={"api-v": "2"}) as response:
                            code = response.status
                            body = await response.json()
                            self.log.debug(f"Auth: code {code}, body {body}")
                            ok = True
                    break
                except Exception as e:
                    self.log.debug(f"Auth: Error `{e}` while auth with `{server_url}`")
                    continue

            if ok:
                if not (body.get("status") is not None and
                        body.get("code") is not None and
                        body.get("msg") is not None):
                    self.log.error("Missing/invalid json members in backend response")
                    raise KeyboardInterrupt

                if test:
                    status = body.get("status")
                    msg = body.get("msg")
                    if status == "2000":
                        self.log.info(f"Authenticated! {msg}")
                    elif status == "200":
                        self.log.info(f"Resumed authenticated session. {msg}")
                    else:
                        self.log.error(f"Backend REFUSED the auth key. Reason: "
                                       f"{msg or 'Backend did not provide a reason'}")
                        self.log.info(f"Server still runnig, but only in Direct connect mode.")
                        self.direct = True
            else:
                self.direct = True
                if test:
                    self.log.error("Cannot auth...")
                if not config.Auth['private']:
                    raise KeyboardInterrupt
                if test:
                    self.log.info(f"Server still runnig, but only in Direct connect mode.")

            if test:
                return ok

            await asyncio.sleep(5)

    async def main(self):
        try:
            self.run = True
            self.tcp = self.tcp(self, self.server_ip, self.server_port)
            self.udp = self.udp(self, self.server_ip, self.server_port)

            # WebApi Start
            if config.WebAPI["enabled"]:
                self.log.debug("Initializing WebAPI...")
                web_thread = Thread(target=self.start_web)
                web_thread.start()
                self.web_thread = web_thread
                self.web_stop = webapp._stop

            # Mods handler
            self.log.debug("Listing mods..")
            if not os.path.exists(self.mods_dir):
                os.mkdir(self.mods_dir)
            for file in os.listdir(self.mods_dir):
                path = os.path.join(self.mods_dir, file).replace("\\", "/")
                if os.path.isfile(path) and path.endswith(".zip"):
                    size = os.path.getsize(path)
                    self.mods_list.append({"path": path, "size": size})
                    self.mods_list[0] += size
            self.log.debug(f"mods_list: {self.mods_list}")
            lmods = len(self.mods_list) - 1
            if lmods > 0:
                self.log.info(f"Loaded {lmods} mods: {round(self.mods_list[0] / MB, 2)}mb")

            await self.authenticate(True)
            tasks = [self.tcp.start(), self.udp.start(), console.start(),
                     self.stop_me(), self.authenticate(),]  #  self.check_alive()
            t = asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

            self.log.info(i18n.start)
            ev.call_event("on_started")
            await t
            # Wait the end.
        except Exception as e:
            self.log.error(f"Exception: {e}")
            traceback.print_exc()
        except KeyboardInterrupt:
            pass
        finally:
            self.run = False

    def start(self):
        asyncio.run(self.main())

    def stop(self):
        self.run = False
        self.log.info(i18n.stop)
        asyncio.run(self.web_stop())
        exit(0)
