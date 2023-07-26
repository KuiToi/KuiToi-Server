# Developed by KuiToi Dev
# File core.core.py
# Written by: SantaSpeen
# Version: 0.4.3
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import os
import random
from threading import Thread

import aiohttp
import uvicorn

from core import utils
from core.Client import Client
from core.tcp_server import TCPServer
from core.udp_server import UDPServer
from modules import PluginsLoader
from modules.WebAPISystem import app as webapp


# noinspection PyProtectedMember
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

        self.lock_upload = False

        self.client_major_version = "2.0"
        self.BeamMP_version = "3.1.1"  # 20.07.2023

        ev.register_event("_get_BeamMP_version", lambda x: tuple([int(i) for i in self.BeamMP_version.split(".")]))
        ev.register_event("_get_player", lambda x: self.get_client(**x['kwargs']))

    def get_client(self, cid=None, nick=None):
        if cid is None and nick is None:
            return None
        if cid is not None:
            if cid == -1:
                return [i for i in self.clients if i is not None]
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
            client._cid = cid
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
        try:
            while self.run:
                await asyncio.sleep(1)
                ca = f"Ss{len(self.clients_by_id)}/{maxp}:{self.get_clients_list()}"
                for client in self.clients:
                    if not client:
                        continue
                    if not client.ready:
                        client.is_disconnected()
                        continue
                    await client._send(ca)
        except Exception as e:
            self.log.error("Error in check_alive.")
            self.log.exception(e)

    async def __gracefully_kick(self):
        for client in self.clients:
            if not client:
                continue
            await client.kick("Server shutdown!")

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
                self.log.info(i18n.core_direct_mode)
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
                data = {"uuid": config.Auth["key"], "players": len(self.clients_by_id),
                        "maxplayers": config.Game["players"], "port": config.Server["server_port"],
                        "map": f"/levels/{config.Game['map']}/info.json", "private": config.Auth['private'],
                        "version": self.BeamMP_version, "clientversion": self.client_major_version,
                        "name": config.Server["name"], "modlist": modlist, "modstotalsize": modstotalsize,
                        "modstotal": modstotal, "playerslist": "", "desc": config.Server['description'], "pass": False}

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
                                ok = True
                        break
                    except Exception as e:
                        self.log.debug(f"Auth: Error `{e}` while auth with `{server_url}`")
                        continue

                if ok:
                    if not (body.get("status") is not None and
                            body.get("code") is not None and
                            body.get("msg") is not None):
                        self.log.error(i18n.core_auth_server_error)
                        return

                    status = body.get("status")
                    msg = body.get("msg")
                    if status == "2000":
                        if test:
                            self.log.debug(f"Authenticated! {msg}")
                    elif status == "200":
                        if test:
                            self.log.debug(f"Resumed authenticated session. {msg}")
                    else:
                        self.log.debug(f"Auth: data {data}")
                        self.log.debug(f"Auth: code {code}, body {body}")

                        self.log.error(i18n.core_auth_server_refused.format(
                            msg or i18n.core_auth_server_refused_no_reason))
                        self.log.info(i18n.core_auth_server_refused_direct_node)
                        self.direct = True
                else:
                    self.direct = True
                    if test:
                        self.log.error(i18n.core_auth_server_no_response)
                        self.log.info(i18n.core_auth_server_refused_direct_node)
                    # if not config.Auth['private']:
                    #     raise KeyboardInterrupt

                if test:
                    return ok

                await asyncio.sleep(5)
            except Exception as e:
                self.log.error(f"Error in heartbeat: {e}")

    async def main(self):
        self.tcp = self.tcp(self, self.server_ip, self.server_port)
        self.udp = self.udp(self, self.server_ip, self.server_port)
        console.add_command(
            "list",
            lambda x: f"Players list: {self.get_clients_list(True)}"
        )

        pl_dir = "plugins"
        self.log.debug("Initializing PluginsLoaders...")
        if not os.path.exists(pl_dir):
            os.mkdir(pl_dir)
        pl = PluginsLoader(pl_dir)
        await pl.load()
        if config.Options['use_lua']:
            from modules.PluginsLoader.lua_plugins_loader import LuaPluginsLoader
            lpl = LuaPluginsLoader(pl_dir)
            lpl.load()

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
            len_mods = len(self.mods_list) - 1
            if len_mods > 0:
                self.log.info(i18n.core_mods_loaded.format(len_mods, round(self.mods_list[0] / MB, 2)))
            self.log.info(i18n.init_ok)

            await self.heartbeat(True)
            for i in range(int(config.Game["players"] * 2.3)):  # * 2.3 For down sock and buffer.
                self.clients.append(None)
            tasks = []
            # self.udp.start,
            f_tasks = [self.tcp.start, self.udp._start, console.start, self.stop_me, self.heartbeat, self.check_alive]
            if config.RCON['enabled']:
                rcon = console.rcon(config.RCON['password'], config.RCON['server_ip'], config.RCON['server_port'])
                f_tasks.append(rcon.start)
            for task in f_tasks:
                tasks.append(asyncio.create_task(task()))
            t = asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

            await ev.call_async_event("_plugins_start")

            self.run = True
            self.log.info(i18n.start)
            ev.call_event("onServerStarted")
            await ev.call_async_event("onServerStarted")
            await t  # Wait end.
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log.error(f"Exception: {e}")
            self.log.exception(e)
        finally:
            self.run = False
            self.tcp.stop()
            self.udp._stop()
            await self.stop()

    def start(self):
        asyncio.run(self.main())

    async def stop(self):
        ev.call_lua_event("onShutdown")
        ev.call_event("onServerStopped")
        await ev.call_async_event("onServerStopped")
        await self.__gracefully_kick()
        if config.Options['use_lua']:
            ev.call_event("_lua_plugins_unload")
        await ev.call_async_event("_plugins_unload")
        self.run = False
        self.log.info(i18n.stop)
        if config.WebAPI["enabled"]:
            asyncio.run(self.web_stop())
