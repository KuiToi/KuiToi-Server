# Developed by KuiToi Dev
# File core.core.py
# Written by: SantaSpeen
# Version 0.1.2
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import struct
from asyncio import StreamWriter, StreamReader

from core import utils


class Core:

    def __init__(self):
        self.log = utils.get_logger("core")
        self.clients = {}
        self.loop = None

    async def tpc_send(self, data, sync):
        pass

    async def tcp_rcv(self, writer: StreamWriter):

        sock = writer.get_extra_info('socket')
        print(writer.transport)
        recv = writer._loop.sock_recv
        header_data = b''
        while True:
            chunk = await recv(sock, 1024)
            if not chunk:
                break
            header_data += chunk
        print(header_data)
        return

    async def kick_client(self, writer: StreamWriter, reason: str):
        self.log.info(
            f"Client: \"IP: {writer.get_extra_info('peername')!r}; Nick: {None}\" - kicked with reason: \"{reason}\"")
        writer.write(b"K" + bytes(reason, "utf-8"))
        await writer.drain()
        writer.close()

    async def auth_client(self, writer: StreamWriter):
        # TODO: Authentication
        addr = writer.get_extra_info('peername')
        self.log.debug(f"Client: \"IP: {addr!r}; Nick: {None}\" - started authentication!")
        data = await self.tcp_rcv(writer)
        self.log.info(data)
        await self.kick_client(writer, "TODO")

    async def tpc_handle_client(self, reader, writer: StreamWriter):
        while True:
            data = await reader.read(2048)
            if not data:
                break
            message = data.decode("utf-8").strip()
            addr = writer.get_extra_info('peername')
            self.log.debug(f"Received {message!r} from {addr!r}")
            code = message[0]
            self.log.debug(f"Client code: {code!r}")
            match code:
                case "C":
                    await self.auth_client(writer)
                case "D":
                    # TODO: HandleDownload
                    await self.kick_client(writer, "TODO: HandleDownload")
                case "P":
                    # TODO: Понять что это и зачем...
                    writer.write(b"P")
                    # writer.close()
                case _:
                    self.log.error(f"Unknown code: {code}")
                    await self.kick_client(writer, "Unknown code")
        await self.kick_client(writer, "Error while connecting..")

    async def tcp_part(self, host, port):
        server = await asyncio.start_server(self.tpc_handle_client, host, port)
        self.loop = server.get_loop()
        print(f"TCP Serving on {server.sockets[0].getsockname()}")
        async with server:
            await server.serve_forever()

    async def udp_part(self, server_ip, server_port):
        pass

    async def main(self):
        server_ip = config.Server["server_ip"]
        server_port = config.Server["server_port"]
        self.log.info("Server started!")

        while True:
            try:
                tasks = [console.start(), self.tcp_part(server_ip, server_port), self.udp_part(server_ip, server_port)]
                await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            except Exception as e:
                await asyncio.sleep(1)
                print("Error: " + str(e))
                # traceback.print_exc()
            except KeyboardInterrupt:
                raise KeyboardInterrupt

    def start(self):
        asyncio.run(self.main())

    def stop(self):
        self.log.info("Goodbye!")
        exit(0)
