# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Core version: 0.2.2
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import traceback

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
        # TODO: i18n
        self.log.info(f"Identifying new ClientConnection...")
        data = await client._recv()
        self.log.debug(f"Version: {data}")
        if data.decode("utf-8") != f"VC{self.Core.client_major_version}":
            # TODO: i18n
            await client.kick("Outdated Version.")
            return False, client
        else:
            await client._tcp_send(b"S")  # Accepted client version

        data = await client._recv()
        self.log.debug(f"Key: {data}")
        if len(data) > 50:
            # TODO: i18n
            await client.kick("Invalid Key (too long)!")
            return False, client
        client._key = data.decode("utf-8")
        ev.call_event("auth_sent_key", client)
        try:
            async with aiohttp.ClientSession() as session:
                url = 'https://auth.beammp.com/pkToUser'
                async with session.post(url, data={'key': client._key}) as response:
                    res = await response.json()
            self.log.debug(f"res: {res}")
            if res.get("error"):
                # TODO: i18n
                await client.kick('Invalid key! Please restart your game.')
                return False, client
            client._nick = res["username"]
            client._roles = res["roles"]
            client._guest = res["guest"]
            # noinspection PyProtectedMember
            client._update_logger()
        except Exception as e:
            # TODO: i18n
            self.log.error(f"Auth error: {e}")
            await client.kick('Invalid authentication data! Try to reconnect in 5 minutes.')
            return False, client

        for _client in self.Core.clients:
            if not _client:
                continue
            if _client.nick == client.nick and _client.guest == client.guest:
                # TODO: i18n
                await client.kick('Stale Client (replaced by new client)')
                return False, client

        ev.call_event("auth_ok", client)

        if len(self.Core.clients_by_id) > config.Game["players"]:
            # TODO: i18n
            await client.kick("Server full!")
            return False, client
        else:
            # TODO: i18n
            self.log.info("Identification success")
            await self.Core.insert_client(client)

        return True, client

    async def set_down_rw(self, reader, writer):
        try:
            cid = (await reader.read(1))[0]
            client = self.Core.get_client(cid=cid)
            if client:
                client._down_rw = (reader, writer)
                self.log.debug(f"Client: {client.nick}:{cid} - HandleDownload!")
            else:
                writer.close()
                self.log.debug(f"Unknown client id:{cid} - HandleDownload")
        finally:
            return

    async def handle_code(self, code, reader, writer):
        match code:
            case "C":
                result, client = await self.auth_client(reader, writer)
                if result:
                    await client._looper()
                return result, client
            case "D":
                await self.set_down_rw(reader, writer)
            case "P":
                writer.write(b"P")
                await writer.drain()
                writer.close()
            case _:
                # TODO: i18n
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
                    await cl._remove_me()
                    del cl
                break
            except Exception as e:
                # TODO: i18n
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
            # TODO: i18n
            self.log.error("Cannot bind port")
            raise e
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log.error(f"Error: {e}")
            raise e
        finally:
            self.run = False
            self.Core.run = False

    def stop(self):
        self.log.debug("Stopping TCP server")
