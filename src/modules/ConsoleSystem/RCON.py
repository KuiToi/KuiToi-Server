import asyncio
import binascii
import hashlib
import os
import zlib
from base64 import b64decode, b64encode

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from core import get_logger


class RCONSystem:
    console = None
    version = "verError"

    def __init__(self, key, host, port):
        self.log = get_logger("RCON")
        self.key = hashlib.sha256(key.encode(config.enc)).digest()
        self.host = host
        self.port = port
        self.run = False

    def _encrypt(self, message):
        self.log.debug(f"Encrypt message: {message}")
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        encoded_data = b64encode(zlib.compress(encrypted_data, level=zlib.Z_BEST_COMPRESSION))
        encoded_iv = b64encode(iv)
        return encoded_iv + b":" + encoded_data

    def _decrypt(self, ciphertext):
        self.log.debug(f"Decrypt message: {ciphertext}")
        encoded_iv, encoded_data = ciphertext.split(b":", 2)
        iv = b64decode(encoded_iv)
        encrypted_data = zlib.decompress(b64decode(encoded_data))
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return unpadded_data

    async def _recv(self, reader, writer) -> tuple[str, bool]:
        try:
            header = b""
            while len(header) < 4:
                h = await reader.read(4 - len(header))
                if not h:
                    break
                else:
                    header += h
            header = int.from_bytes(header, byteorder='little', signed=True)
            if header <= 0:
                self.log.warning("Connection closed!")
                writer.close()

            encrypted_data = b""
            while len(encrypted_data) < header:
                buffer = await reader.read(header - len(encrypted_data))
                if not buffer:
                    break
                else:
                    encrypted_data += buffer
            try:
                data, s = self._decrypt(encrypted_data), True
            except binascii.Error:
                data, s = encrypted_data, False
            except ValueError:
                data, s = encrypted_data, False

            self.log.debug(f"Received: {data}, {s}")
            return data.decode(config.enc), s
        except ConnectionResetError:
            self.log.warning("Connection reset.")
            return "", False

    async def _send(self, data, writer, encrypt=True, warn=True):
        self.log.debug(f"Sending: \"{data}\"")
        if isinstance(data, str):
            data = data.encode(config.enc)

        if encrypt:
            data = self._encrypt(data)
            self.log.debug(f"Send encrypted: {data}")

        header = len(data).to_bytes(4, "little", signed=True)
        try:
            writer.write(header + data)
            await writer.drain()
            return True
        except ConnectionError:
            self.log.debug("Sending error...")
            if encrypt and warn:
                self.log.warning("Connection closed!")
            return False

    async def send_hello(self, writer, work):
        while work[0]:
            await asyncio.sleep(5)
            if not await self._send("Cs:hello", writer, warn=False):
                work[0] = False
                writer.close()
                break

    async def while_handle(self, reader, writer):
        ver, status = await self._recv(reader, writer)
        if ver == "ver" and status:
            await self._send(self.version, writer)
        cmds, status = await self._recv(reader, writer)
        if cmds == "commands" and status:
            await self._send("SKIP", writer)
        work = [True]
        t = asyncio.create_task(self.send_hello(writer, work))
        while work[0]:
            data, status = await self._recv(reader, writer)
            if not status:
                work[0] = False
                writer.close()
                break
            code = data[:2]
            message = data[data.find(":") + 1:]
            match code:
                case "Cs":
                    match message:
                        case "hello":
                            await self._send("Os:hello", writer)
                        case _:
                            self.log.warning(f"Unknown command: {data}")
                case "C:":
                    self.log.info(f"Called the command: {message}")
                    if message == "exit":
                        self.log.info("Connection closed.")
                        writer.close()
                        work[0] = False
                        break

                case "Os":
                    match message:
                        case "hello":
                            pass
                            # await self._send("Cs:hello", writer)
                        case _:
                            self.log.warning(f"Unknown command: {data}")
                case "O:":
                    pass
                case _:
                    self.log.warning(f"Unknown command: {data}")

        await t

    async def handle_connect(self, reader, writer):
        try:
            hello, status = await self._recv(reader, writer)
            if hello == "hello" and status:
                await self._send("hello", writer)
                await self.while_handle(reader, writer)
            else:
                await self._send("E:Wrong password", writer, False)
                writer.close()
        except Exception as e:
            self.log.error("Error while handling connection...")
            self.log.exception(e)

    async def start(self):
        self.run = True
        try:
            server = await asyncio.start_server(self.handle_connect, self.host, self.port, backlog=5)
            self.log.info(f"RCON server started on {server.sockets[0].getsockname()!r}")
            async with server:
                await server.serve_forever()
        except OSError as e:
            self.log.error(i18n.core_bind_failed.format(e))
            raise e
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.log.error(f"Error: {e}")
            raise e
        finally:
            self.run = False
