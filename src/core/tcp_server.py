# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Version 0.1.2
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import socket
import traceback

from core import utils


class TCPServer:
    def __init__(self, core, host, port):
        self.log = utils.get_logger("TCPServer")
        self.Core = core
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()

    async def recv(self, client):
        # if not client.is_disconnected():
        #     self.log.debug(f"Client with {client.nick}({client.cid}) disconnected")
        #     return

        header = await client.reader.read(4)  # header: 4 bytes
        data = await client.reader.read(101 * MB)

        int_header = 0
        for i in range(len(header)):
            int_header += header[i]
        self.log.debug(f"header: `{header}`; int_header: `{int_header}`; data: `{data}`;")

        if int_header <= 0:
            await client.kick("Invalid packet - header negative")
            return

        if not int_header < 100 * MB:
            await client.kick("Header size limit exceeded")
            self.log.warn(f"Client {client.nick}({client.cid}) sent header of >100MB - "
                          f"assuming malicious intent and disconnecting the client.")
            return

        if len(data) != int_header:
            self.log.debug(f"WARN Expected to read {int_header} bytes, instead got {len(data)}")

        # TODO: ABG: DeComp(Data)
        abg = b"ABG:"
        if len(data) > len(abg) and data.startswith(abg):
            data = data[len(abg):]
            # return DeComp(Data);
        return data

    async def auth_client(self, sock):
        # TODO: Authentication
        client = self.Core.create_client(sock)
        self.log.debug(f"Client: \"IP: {client.addr!r}; ID: {client.cid}\" - Authentication!")
        data = await self.recv(client)
        self.log.debug(f"recv1 data: {data}")
        if len(data) > 50:
            client.kick("Too long data")
            return
        if "VC2.0" not in data.decode("utf-8"):
            client.kick("Outdated Version.")
            return
        else:
            pass
            # self.log.debug('tcp_send(b"A")')
            # client.tcp_send(b"A")

        # data = await self.recv(client)
        # self.log.debug(f"recv2 data: {data}")

        client.kick("TODO Authentication")
        return False

    async def handle_download(self, sock):
        # TODO: HandleDownload
        self.log.debug(f"Client: \"IP: {0!r}; ID: {0}\" - HandleDownload!")
        return False

    async def handle_code(self, code, sock):
        match code:
            case "C":
                return await self.auth_client(sock)
            case "D":
                return await self.handle_download(sock)
            case "P":
                sock.send(b"P")
                return True
            case _:
                self.log.error(f"Unknown code: {code}")
                return False

    async def handle_client(self, sock):
        while True:
            try:
                data = sock.recv(1)
                if not data:
                    break
                code = data.decode()
                self.log.debug(f"Received {code!r} from {sock.getsockname()!r}")
                if not await self.handle_code(code, sock):
                    break
            except Exception as e:
                self.log.error(f"Error: {e}")
                traceback.print_exc()
                break
        sock.close()
        self.log.error("Error while connecting..")

    async def start(self):
        self.log.debug("Starting TCP server.")
        server = await asyncio.start_server(self.handle_client, self.host, self.port, backlog=config.Game["players"]+1)
        try:
            self.log.debug(f"TCP server started on {server.sockets[0].getsockname()!r}")
            while True:
                async with server:
                    await server.serve_forever()
        except Exception as e:
            self.log.error(f"Error: {e}")
            traceback.print_exc()
        finally:
            await self.stop()

    async def stop(self):
        self.log.debug("Stopping TCP server")
