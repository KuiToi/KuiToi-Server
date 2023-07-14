# Developed by KuiToi Dev
# File core.core.py
# Written by: SantaSpeen
# Core version: 0.2.1
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import math
import os
import random
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
        self.down_rw = (None, None)
        self.log = utils.get_logger("client(None:0)")
        self.addr = writer.get_extra_info("sockname")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.cid = -1
        self.key = None
        self.nick = None
        self.roles = None
        self.guest = True
        self.alive = True
        self.ready = False

    def _update_logger(self):
        self.log = utils.get_logger(f"{self.nick}:{self.cid})")
        self.log.debug(f"Update logger")

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
        if not self.alive:
            self.log.debug(f"Kick({reason}) skipped;")
            return
        self.log.info(f"Kicked with reason: \"{reason}\"")
        await self.tcp_send(b"K" + bytes(reason, "utf-8"))
        self.alive = False
        # await self.remove_me()

    async def tcp_send(self, data, to_all=False, writer=None):

        # TNetwork.cpp; Line: 383
        # BeamMP TCP protocol sends a header of 4 bytes, followed by the data.
        # [][][][][][]...[]
        # ^------^^---...-^
        #  size     data

        if writer is None:
            writer = self.writer

        if to_all:
            for client in self.Core.clients:
                if not client:
                    continue
                await client.tcp_send(data)
            return

        # self.log.debug(f"tcp_send({data})")
        if len(data) == 10:
            data += b"."
        header = len(data).to_bytes(4, "little", signed=True)
        self.log.debug(f'len: {len(data)}; send: {header + data}')
        try:
            writer.write(header + data)
            await writer.drain()
        except ConnectionError:
            self.log.debug('tcp_send: Disconnected')
            self.alive = False

    async def recv(self):
        try:
            header = await self.reader.read(4)  # header: 4 bytes

            int_header = 0
            for i in range(len(header)):
                int_header += header[i]

            if int_header <= 0:
                await asyncio.sleep(0.1)
                self.is_disconnected()
                if self.alive:
                    self.log.debug(f"Header: {header}")
                    await self.kick("Invalid packet - header negative")
                return b""

            if int_header > 100 * MB:
                await self.kick("Header size limit exceeded")
                self.log.warn(f"Client {self.nick}:{self.cid} sent header of >100MB - "
                              f"assuming malicious intent and disconnecting the client.")
                return b""

            data = await self.reader.read(100 * MB)
            self.log.debug(f"header: `{header}`; int_header: `{int_header}`; data: `{data}`;")

            if len(data) != int_header:
                self.log.debug(f"WARN Expected to read {int_header} bytes, instead got {len(data)}")

            abg = b"ABG:"
            if len(data) > len(abg) and data.startswith(abg):
                data = zlib.decompress(data[len(abg):])
                self.log.debug(f"ABG: {data}")
                return data
            return data
        except ConnectionError:
            self.alive = False
            return b""

    async def _split_load(self, start, end, d_sock, filename):
        real_size = end - start
        writer = self.down_rw[1] if d_sock else self.writer
        who = 'dwn' if d_sock else 'srv'
        self.log.debug(f"[{who}] Real size: {real_size/MB}mb; {real_size == end}, {real_size*2 == end}")

        with open(filename, 'rb') as f:
            f.seek(start)
            data = f.read(end)
            try:
                writer.write(data)
                await writer.drain()
                self.log.debug(f"[{who}] File sent.")
            except ConnectionError:
                self.alive = False
                self.log.debug(f"[{who}] Disconnected.")
        #         break
        return real_size

        # chunk_size = 125 * MB
        # if chunk_size > real_size:
        #     chunk_size = real_size
        # chunks = math.floor(real_size / chunk_size)
        # self.log.debug(f"[{who}] s:{start}, e:{end}, c:{chunks}, cz:{chunk_size/MB}mb, rs:{real_size/MB}mb")
        # dw = 0
        # for chunk in range(1, chunks + 1):
        #     chunk_end = start + (chunk_size * chunk)
        #     chunk_start = chunk_end - chunk_size
        #     # if chunk_start != 0:
        #     #     chunk_start -= 1
        #     real_size -= chunk_size
        #     if chunk_size > real_size:
        #         chunk_end = real_size
        #     self.log.debug(f"[{who}] Chunk: {chunk}; Start: {chunk_start}; End: {chunk_end/MB};")
        #     with open(filename, 'rb') as f:
        #         f.seek(chunk_start)
        #         data = f.read(chunk_end)
        #         try:
        #             writer.write(data)
        #             await writer.drain()
        #         except ConnectionError:
        #             self.alive = False
        #             self.log.debug(f"[{who}] Disconnected")
        #             break
        #         dw += len(data)
        #         del data
        # self.log.debug(f"[{who}] File sent.")
        # return dw

    async def sync_resources(self):
        while self.alive:
            data = await self.recv()
            self.log.debug(f"data: {data!r}")
            if data.startswith(b"f"):
                file = data[1:].decode("utf-8")
                self.log.debug(f"Sending File: {file}")
                size = -1
                for mod in self.Core.mods_list:
                    if type(mod) == int:
                        continue
                    if mod.get('path') == file:
                        size = mod['size']
                        self.log.debug("File is accept.")
                        break
                if size == -1:
                    await self.tcp_send(b"CO")
                    await self.kick(f"Not allowed mod: " + file)
                    return
                await self.tcp_send(b"AG")
                t = 0
                while not self.down_rw[0]:
                    await asyncio.sleep(0.1)
                    t += 1
                    if t > 50:
                        await self.kick("Missing download socket")
                        return
                self.log.info(f"Requested mode: {file!r}")
                self.log.debug(f"Mode size: {size/MB}")

                msize = math.floor(size / 2)
                # uploads = [
                #     asyncio.create_task(self._split_load(0, msize, False, file)),  # SplitLoad_0
                #     asyncio.create_task(self._split_load(msize, size, True, file))  # SplitLoad_1
                # ]
                # await asyncio.wait(uploads)
                uploads = [
                    self._split_load(0, msize, False, file),
                    self._split_load(msize, size, True, file)
                ]
                sl0, sl1 = await asyncio.gather(*uploads)
                sent = sl0 + sl1
                ok = sent == size
                lost = size - sent
                self.log.debug(f"SplitLoad_0: {sl0}; SplitLoad_1: {sl1}; At all ({ok}): Sent: {sent}; Lost: {lost}")
                self.log.debug(f"SplitLoad_0: {sl0/MB}mb; "
                               f"SplitLoad_1: {sl1/MB}MB; At all ({ok}): Sent: {sent/MB}mb; Lost: {lost/MB}mb")
                if not ok:
                    self.alive = False
                    self.log.error(f"Error while sending.")
                    return
            elif data.startswith(b"SR"):
                path_list = ''
                size_list = ''
                for mod in self.Core.mods_list:
                    if type(mod) == int:
                        continue
                    path_list += f"{mod['path']};"
                    size_list += f"{mod['size']};"
                mod_list = path_list + size_list
                self.log.debug(f"Mods List: {mod_list}")
                if len(mod_list) == 0:
                    await self.tcp_send(b"-")
                else:
                    await self.tcp_send(bytes(mod_list, "utf-8"))
            elif data == b"Done":
                await self.tcp_send(b"M/levels/" + bytes(config.Game['map'], 'utf-8') + b"/info.json")
                break
        return

    async def looper(self):
        await self.tcp_send(b"P" + bytes(f"{self.cid}", "utf-8"))  # Send clientID
        await self.sync_resources()
        while self.alive:
            data = await self.recv()
            if data == b"":
                if not self.alive:
                    break
                else:
                    await asyncio.sleep(.2)
                    self.is_disconnected()
                    continue
            code = data.decode()[0]
            self.log.debug(f"Received code: {code}, data: {data}")
            match code:
                case "H":
                    # Client connected
                    self.ready = True
                    await self.tcp_send(b"Sn" + bytes(self.nick, "utf-8"), to_all=True)
                case "C":
                    # Chat
                    await self.tcp_send(data, to_all=True)

    async def remove_me(self):
        await asyncio.sleep(0.3)
        self.alive = False
        if (self.cid > 0 or self.nick is not None) and \
                self.Core.clients_by_nick.get(self.nick):
            # if self.ready:
            #     await self.tcp_send(b"", to_all=True)  # I'm disconnected.
            self.log.debug(f"Removing client {self.nick}:{self.cid}")
            self.log.info("Disconnected")
            self.Core.clients[self.cid] = None
            self.Core.clients_by_id.pop(self.cid)
            self.Core.clients_by_nick.pop(self.nick)
        else:
            self.log.debug(f"Removing client; Closing connection...")
        if not self.writer.is_closing():
            self.writer.close()
        _, down_w = self.down_rw
        if down_w and not down_w.is_closing():
            down_w.close()


class Core:

    def __init__(self):
        self.log = utils.get_logger("core")
        self.loop = asyncio.get_event_loop()
        self.run = False
        self.direct = False
        self.clients = []
        self.clients_by_id = {}
        self.clients_by_nick = {}
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
        self.BeamMP_version = "3.2.0"

    def get_client(self, cid=None, nick=None):
        if cid is not None:
            return self.clients_by_id.get(cid)
        if nick:
            return self.clients_by_nick.get(nick)

    async def insert_client(self, client):
        await asyncio.sleep(random.randint(3, 9) * 0.01)
        cid = 0
        for _client in self.clients:
            if not _client:
                break
            if _client.cid == cid:
                cid += 1
            else:
                break
        await asyncio.sleep(random.randint(3, 9) * 0.01)
        if not self.clients[cid]:
            client.cid = cid
            self.clients_by_nick.update({client.nick: client})
            self.log.debug(f"Inserting client: {client.nick}:{client.cid}")
            self.clients_by_id.update({client.cid: client})
            self.clients[client.cid] = client
            # noinspection PyProtectedMember
            client._update_logger()
            return
        await self.insert_client(client)

    def create_client(self, *args, **kwargs):
        self.log.debug(f"Create client")
        client = Client(core=self, *args, **kwargs)
        return client

    def get_clients_list(self, need_cid=False):
        out = ""
        for client in self.clients:
            if not client:
                continue
            out += f"{client.nick}"
            if need_cid:
                out += f":{client.cid}"
            out += ","
        if out:
            out = out[:-1]
        return out

    async def check_alive(self):
        maxp = config.Game['players']
        while self.run:
            await asyncio.sleep(1)
            ca = f"Ss{len(self.clients_by_id)}/{maxp}:{self.get_clients_list()}"
            for client in self.clients:
                if not client:
                    continue
                if not client.ready:
                    client.is_disconnected()
                    continue
                await client.tcp_send(bytes(ca, "utf-8"))

    @staticmethod
    def start_web():
        uvconfig = uvicorn.Config("modules.WebAPISystem.app:web_app",
                                  host=config.WebAPI["server_ip"],
                                  port=config.WebAPI["server_port"],
                                  loop="asyncio")
        uvserver = uvicorn.Server(uvconfig)
        webapp.uvserver = uvserver
        uvserver.run()

    async def stop_me(self):
        while webapp.data_run[0]:
            await asyncio.sleep(1)
        self.run = False
        raise KeyboardInterrupt

    # noinspection SpellCheckingInspection,PyPep8Naming
    async def heartbeat(self, test=False):
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
            try:
                data = {"uuid": config.Auth["key"], "players": len(self.clients), "maxplayers": config.Game["players"],
                        "port": config.Server["server_port"], "map": f"/levels/{config.Game['map']}/info.json",
                        "private": config.Auth['private'], "version": self.BeamMP_version,
                        "clientversion": self.client_major_version,
                        "name": config.Server["name"], "modlist": modlist, "modstotalsize": modstotalsize,
                        "modstotal": modstotal, "playerslist": "", "desc": config.Server['description'], "pass": False}
                self.log.debug(f"Auth: data {data}")

                # Sentry?
                ok = False
                body = {}
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
            except Exception as e:
                self.log.error(f"Error in heartbeat: {e}")

    async def main(self):
        self.run = True
        self.tcp = self.tcp(self, self.server_ip, self.server_port)
        self.udp = self.udp(self, self.server_ip, self.server_port)
        console.add_command(
            "list",
            lambda x: f"Players list: {self.get_clients_list(True)}"
        )
        try:
            # WebApi Start
            if config.WebAPI["enabled"]:
                self.log.debug("Initializing WebAPI...")
                web_thread = Thread(target=self.start_web, name="WebApiThread")
                web_thread.start()
                self.log.debug(f"WebAPI started at new thread: {web_thread.name}")
                self.web_thread = web_thread
                # noinspection PyProtectedMember
                self.web_stop = webapp._stop
                await asyncio.sleep(.3)

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

            await self.heartbeat(True)
            for i in range(int(config.Game["players"] * 1.3)):
                self.clients.append(None)
            tasks = []
            # self.udp.start,
            nrtasks = [self.tcp.start, console.start, self.stop_me, self.heartbeat, self.check_alive]
            for task in nrtasks:
                tasks.append(asyncio.create_task(task()))
            t = asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

            self.log.info(i18n.start)
            ev.call_event("on_started")
            await t
            # Wait the end.
        except Exception as e:
            self.log.error(f"Exception: {e}")
            self.log.exception(e)
        except KeyboardInterrupt:
            pass
        finally:
            self.tcp.stop()
            # self.udp.stop()
            self.run = False

    def start(self):
        asyncio.run(self.main())

    def stop(self):
        self.run = False
        self.log.info(i18n.stop)
        if config.WebAPI["enabled"]:
            asyncio.run(self.web_stop())
        exit(0)
