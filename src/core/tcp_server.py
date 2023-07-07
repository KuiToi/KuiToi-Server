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

    async def recv(self, client):
        if not client.is_disconnected():
            self.log.debug(f"Client with {client.nick}({client.cid}) disconnected")
            return

        header = await client.loop.sock_recv(client.socket, 4)  # header: 4 bytes
        data = b""
        while True:
            chunk = await client.loop.sock_recv(client.socket, 1)
            if not chunk:
                break
            data += chunk

        int_header = 0
        for i in range(len(header)):
            int_header += header[i]
        self.log.debug(f"header: `{header}`; int_header: `{int_header}`; data: `{data}`;")

        if int_header <= 0:
            client.kick("Invalid packet - header negative")
            return

        if not int_header < 100 * MB:
            client.kick("Header size limit exceeded")
            self.log.warn(f"Client {client.nick}({client.cid}) sent header of >100MB - "
                          f"assuming malicious intent and disconnecting the client.")
            return

        # TODO: read Data
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
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(config.Game["players"])
        self.log.debug(f"Serving on {server_socket.getsockname()}")
        server_socket.setblocking(False)
        loop = asyncio.get_event_loop()
        while True:
            sock, _ = await loop.sock_accept(server_socket)
            loop.create_task(self.handle_client(sock))
