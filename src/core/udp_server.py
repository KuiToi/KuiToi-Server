# Developed by KuiToi Dev
# File core.udp_server.py
# Written by: SantaSpeen
# Version 0.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import traceback

from core import utils


class UDPServer:

    def __init__(self, core, host, port):
        self.log = utils.get_logger("UDPServer")
        self.Core = core
        self.host = host
        self.port = port
        self.loop = asyncio.get_event_loop()

    async def handle_client(self, srv_sock):
        while True:
            try:
                data, addr = await self.loop.sock_recv(srv_sock, 1024)
                if not data:
                    break
                code = data.decode()
                self.log.debug(f"Received {code!r} from {addr!r}")
                # if not await self.handle_code(code, sock):
                #     break
            except Exception as e:
                self.log.error(f"Error: {e}")
                traceback.print_exc()
                break
        srv_sock.close()
        self.log.error("Error while connecting..")

    async def start(self):
        self.log.debug("Starting UDP server.")
        await self.stop()
        # srv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # srv_sock.bind((self.host, self.port))
        # self.log.debug(f"Serving on {srv_sock.getsockname()}")
        # try:
        #     await self.handle_client(srv_sock)
        # except Exception as e:
        #     self.log.error(f"Error: {e}")
        #     traceback.print_exc()
        # finally:
        #     await self.stop()

    async def stop(self):
        self.log.debug("Stopping UDP server")
