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
        cid = data[0] - 1
        code = data[2:3].decode()

        client = self.Core.get_client(cid=cid)
        if client:
            if client._udp_sock != (self.transport, addr):
                client._udp_sock = (self.transport, addr)
                self.log.debug(f"Set UDP Sock for CID: {cid}")
        else:
            self.log.debug(f"Client not found.")

        match code:
            case "p":
                self.log.debug(f"[{cid}] Send ping")
                # TODO: Call event onSentPing
                self.transport.sendto(b"p", addr)  # Send ping
            case "Z":
                if client:
                    client._send(data)
                # TODO: Call event onChangePosition
                pass
            case _:
                self.log.debug(f"[{cid}] Unknown code: {code}")

    def connection_lost(self, exc):
        if exc is not None and exc != KeyboardInterrupt:
            self.log.debug(f'Connection raised: {exc}')
        self.log.debug(f'Disconnected.')
        self.transport.close()

    async def _start(self):
        self.log.debug("Starting UDP server.")
        self.run = True
        try:
            self.transport, _ = await self.loop.create_datagram_endpoint(
                lambda: UDPServer(self.Core),
                local_addr=(self.host, self.port)
            )
            self.log.debug(f"UDP server started on {self.transport.get_extra_info('sockname')}")
            return
        except OSError as e:
            self.run = False
            self.Core.run = False
            self.log.error("Cannot bind port or other error")
            self.log.exception(e)
        except Exception as e:
            self.run = False
            self.Core.run = False
            self.log.error(f"Error: {e}")
            self.log.exception(e)

    def _stop(self):
        self.log.debug("Stopping UDP server")
        self.transport.close()
