# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Version 0.2.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import traceback
from asyncio import AbstractEventLoop
from threading import Thread

import aiohttp

from core import utils


class TCPServer:
    def __init__(self, core, host, port):
        self.log = utils.get_logger("TCPServer")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.host = host
        self.port = port
        self.run = False

    async def auth_client(self, reader, writer):
        client = self.Core.create_client(reader, writer)
        self.log.info(f"Identifying new ClientConnection...")
        data = await client.recv()
        self.log.debug(f"recv1 data: {data}")
        if data.decode("utf-8") != f"VC{self.Core.client_major_version}":
            await client.kick("Outdated Version.")
            return False, None
        else:
            await client.tcp_send(b"S")  # Accepted client version

        data = await client.recv()
        self.log.debug(f"recv2 data: {data}")
        if len(data) > 50:
            await client.kick("Invalid Key (too long)!")
            return False, None
        client.key = data.decode("utf-8")
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://auth.beammp.com/pkToUser'
                async with session.post(url, data={'key': client.key}) as response:
                    res = await response.json()
            self.log.debug(f"res: {res}")
            if res.get("error"):
                await client.kick('Invalid key! Please restart your game.')
                return False, None
            client.nick = res["username"]
            client.roles = res["roles"]
            client.guest = res["guest"]
            client._update_logger()
        except Exception as e:
            self.log.error(f"Auth error: {e}")
            await client.kick('Invalid authentication data! Try to reconnect in 5 minutes.')
            return False, None

        for _client in self.Core.clients:
            if not _client:
                continue
            if _client.nick == client.nick and _client.guest == client.guest:
                await client.kick('Stale Client (replaced by new client)')
                return False, None

        ev.call_event("on_auth", client)

        if len(self.Core.clients_by_id) > config.Game["players"]:
            await client.kick("Server full!")
            return False, None
        else:
            self.log.info("Identification success")
            await self.Core.insert_client(client)

        return True, client

    async def set_down_rw(self, reader, writer):
        try:
            cid = (await reader.read(1))[0]
            ok = False
            for _client in self.Core.clients:
                if not _client:
                    continue
                if _client.cid == cid:
                    _client.down_rw = (reader, writer)
                    ok = True
                    self.log.debug(f"Client: {_client.nick}:{cid} - HandleDownload!")
            if not ok:
                writer.close()
                self.log.debug(f"Unknown client - HandleDownload")
        finally:
            return

    async def handle_code(self, code, reader, writer):
        match code:
            case "C":
                result, client = await self.auth_client(reader, writer)
                if result:
                    await client.looper()
                return result, client
            case "D":
                await self.set_down_rw(reader, writer)
            case "P":
                writer.write(b"P")
                await writer.drain()
                writer.close()
            case _:
                self.log.error(f"Unknown code: {code}")
                writer.close()
        return False, None

    async def handle_client(self, reader, writer):
        while True:
            try:
                data = await reader.read(1)
                if not data:
                    break
                code = data.decode()
                self.log.debug(f"Received {code!r} from {writer.get_extra_info('sockname')!r}")
                # task = asyncio.create_task(self.handle_code(code, reader, writer))
                # await asyncio.wait([task], return_when=asyncio.FIRST_EXCEPTION)
                _, cl = await self.handle_code(code, reader, writer)
                if cl:
                    await cl.remove_me()
                break
            except Exception as e:
                self.log.error("Error while connecting..")
                self.log.exception(e)
                traceback.print_exc()
                break

    async def start(self):
        self.log.debug("Starting TCP server.")
        self.run = True
        try:
            server = await asyncio.start_server(self.handle_client, self.host, self.port,
                                                backlog=int(config.Game["players"] * 1.3))
            self.log.debug(f"TCP server started on {server.sockets[0].getsockname()!r}")
            while True:
                async with server:
                    await server.serve_forever()
        except OSError as e:
            self.log.error("Cannot bind port")
            raise e
        except BaseException as e:
            self.log.error(f"Error: {e}")
            raise e
        finally:
            self.run = False
            self.Core.run = False

    def stop(self):
        self.log.debug("Stopping TCP server")
