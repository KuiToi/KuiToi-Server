# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Version 0.1.6
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import traceback

import aiohttp

from core import utils


class TCPServer:
    def __init__(self, core, host, port):
        self.log = utils.get_logger("TCPServer")
        self.Core = core
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()

    async def auth_client(self, reader, writer):
        client = self.Core.create_client(reader, writer)
        self.log.info(f"Identifying new ClientConnection...")
        data = await client.recv()
        self.log.debug(f"recv1 data: {data}")
        if len(data) > 50:
            await client.kick("Too long data")
            return False, None
        if "VC2.0" not in data.decode("utf-8"):
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
        async with aiohttp.ClientSession() as session:
            url = 'https://auth.beammp.com/pkToUser'
            async with session.post(url, data={'key': client.key}) as response:
                res = await response.json()
        self.log.debug(f"res: {res}")
        try:
            if res.get("error"):
                await client.kick('Invalid key! Please restart your game.')
                return
            client.nick = res["username"]
            client.roles = res["roles"]
            client.guest = res["guest"]
            client._update_logger()
        except Exception as e:
            self.log.error(f"Auth error: {e}")
            await client.kick('Invalid authentication data! Try to connect in 5 minutes.')

        # TODO: Password party
        # await client.tcp_send(b"S")  # Ask client key (How?)

        ev.call_event("on_auth", client)

        if len(self.Core.clients) > config.Game["players"]:
            await client.kick("Server full!")
        else:
            self.log.info("Identification success")
            self.Core.insert_client(client)

        return True, client

    async def handle_download(self, writer):
        # TODO: HandleDownload
        self.log.debug(f"Client: \"IP: {0!r}; ID: {0}\" - HandleDownload!")
        return False

    async def handle_code(self, code, reader, writer):
        match code:
            case "C":
                result, client = await self.auth_client(reader, writer)
                if result:
                    await client.sync_resources()
                    # await client.kick("Authentication success! Server not ready.")
                    return True
                return False
            case "D":
                return await self.handle_download(writer)
            case "P":
                writer.write(b"P")
                await writer.drain()
                return True
            case _:
                self.log.error(f"Unknown code: {code}")
                return False

    async def handle_client(self, reader, writer):
        while True:
            try:
                data = await reader.read(1)
                if not data:
                    break
                code = data.decode()
                self.log.debug(f"Received {code!r} from {writer.get_extra_info('sockname')!r}")
                result = await self.handle_code(code, reader, writer)
                if not result:
                    break
            except Exception as e:
                self.log.error("Error while connecting..")
                self.log.error(f"Error: {e}")
                traceback.print_exc()
                break

    async def start(self):
        self.log.debug("Starting TCP server.")
        try:
            server = await asyncio.start_server(self.handle_client, self.host, self.port,
                                                backlog=config.Game["players"] + 1)
        except OSError as e:
            self.log.error(f"Error: {e}")
            self.Core.run = False
            raise e
        self.log.debug(f"TCP server started on {server.sockets[0].getsockname()!r}")
        while True:
            async with server:
                await server.serve_forever()

    def stop(self):
        self.log.debug("Stopping TCP server")
