# Developed by KuiToi Dev
# File core.udp_server.py
# Written by: SantaSpeen
# Core version: 0.3.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import traceback

from core import utils


class UDPServer(asyncio.DatagramTransport):

    def __init__(self, core, host=None, port=None):
        super().__init__()
        self.log = utils.get_logger("UDPServer")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.host = host
        self.port = port
        self.run = False
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.transport.sendto(data, addr)

    async def start(self):
        self.log.debug("Starting UDP server.")
        self.run = True
        try:
            self.transport, _ = await self.loop.create_datagram_endpoint(
                lambda: self,
                local_addr=(self.host, self.port),
                reuse_port=True
            )
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
        self.transport.close()
