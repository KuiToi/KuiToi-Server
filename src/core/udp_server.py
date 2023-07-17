# Developed by KuiToi Dev
# File core.udp_server.py
# Written by: SantaSpeen
# Core version: 0.3.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import traceback

from core import utils


class UDPServer:

    def __init__(self, core, host, port):
        self.log = utils.get_logger("UDPServer")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.host = host
        self.port = port
        self.run = False

    async def handle_client(self, reader, writer):
        while True:
            try:
                data = await reader.read(1)
                if not data:
                    break
                code = data.decode()
                self.log.debug(f"Received {code!r} from {writer.get_extra_info('sockname')!r}")
                # await self.handle_code(code, reader, writer)
                # task = asyncio.create_task(self.handle_code(code, reader, writer))
                # await asyncio.wait([task], return_when=asyncio.FIRST_EXCEPTION)
                if not writer.is_closing():
                    writer.close()
                self.log.debug("Disconnected.")
                break
            except Exception as e:
                self.log.error("Error while connecting..")
                self.log.error(f"Error: {e}")
                traceback.print_exc()
                break

    async def start(self):
        self.log.debug("Starting UDP server.")
        self.run = True
        try:
            pass
        except OSError as e:
            self.log.error("Cannot bind port or other error")
            raise e
        except BaseException as e:
            self.log.error(f"Error: {e}")
            raise e
        finally:
            self.run = False
            self.Core.run = False

    def stop(self):
        self.log.debug("Stopping UDP server")
