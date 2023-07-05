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

    async def send(self, data, sync):
        pass

    async def recv(self, client):
        not_alive = client.is_disconnected()
        if not not_alive:
            self.log.debug(f"Client with ID {client.cid} disconnected")
            return ""
        data = b""
        while True:
            chunk = await client.loop.sock_recv(client.socket, 10)
            if not chunk:
                break
            data += chunk
        return data

    async def auth_client(self, sock):
        # TODO: Authentication
        client = self.Core.create_client(sock)
        self.log.debug(f"Client: \"IP: {client.addr!r}; ID: {client.cid}\" - started authentication!")
        data = await self.recv(client)
        self.log.debug(f"recv1 data: {data}")
        if len(data) > 50:
            client.kick("Too long data")
            return
        if "VC2.0" not in data.decode("utf-8"):
            client.kick("Outdated Version.")
            return
        else:
            self.log.debug('tcp_send(b"A")')
            client.tcp_send(b"A")

        data = await self.recv(client)
        self.log.debug(f"recv2 data: {data}")

        client.kick("TODO Authentication")

    async def handle_client(self, sock):

        while True:
            try:
                data = sock.recv(1)
                if not data:
                    break
                message = data.decode("utf-8").strip()
                addr = sock.getsockname()
                self.log.debug(f"Received {message!r} from {addr!r}")
                code = message[0]
                match code:
                    case "C":
                        await self.auth_client(sock)
                    case "D":
                        # TODO: HandleDownload
                        print("TODO: HandleDownload")
                    case "P":
                        # TODO: Понять что это и зачем...
                        sock.sendall(b"P")
                    case _:
                        self.log.error(f"Unknown code: {code}")
            except Exception as e:
                print("Error:", e)
                traceback.print_exc()
                break
        print("Error while connecting..")

    # async def start(self):
    #     self.log.debug("Starting TCP server.")
    #     server = await asyncio.start_server(self.handle_client, self.host, self.port, family=socket.AF_INET)
    #     self.log.debug(f"Serving on {server.sockets[0].getsockname()}")
    #     async with server:
    #         await server.serve_forever()

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
