import asyncio
import math
import zlib

from core import utils


class Client:

    def __init__(self, reader, writer, core):
        self.reader = reader
        self.writer = writer
        self.down_rw = (None, None)
        self.log = utils.get_logger("client(None:0)")
        self.addr = writer.get_extra_info("sockname")
        self.loop = asyncio.get_event_loop()
        self.Core = core
        self.cid = -1
        self.key = None
        self.nick = None
        self.roles = None
        self.guest = True
        self.alive = True
        self.ready = False

    def _update_logger(self):
        self.log = utils.get_logger(f"{self.nick}:{self.cid})")
        self.log.debug(f"Update logger")

    def is_disconnected(self):
        if not self.alive:
            return True
        res = self.writer.is_closing()
        if res:
            self.log.debug(f"Disconnected.")
            self.alive = False
            return True
        else:
            self.log.debug(f"Alive.")
            self.alive = True
            return False

    async def kick(self, reason):
        if not self.alive:
            self.log.debug(f"Kick({reason}) skipped;")
            return
        # TODO: i18n
        self.log.info(f"Kicked with reason: \"{reason}\"")
        await self.tcp_send(b"K" + bytes(reason, "utf-8"))
        self.alive = False

    async def tcp_send(self, data, to_all=False, writer=None):

        # TNetwork.cpp; Line: 383
        # BeamMP TCP protocol sends a header of 4 bytes, followed by the data.
        # [][][][][][]...[]
        # ^------^^---...-^
        #  size     data

        if writer is None:
            writer = self.writer

        if to_all:
            for client in self.Core.clients:
                if not client:
                    continue
                await client.tcp_send(data)
            return

        if len(data) == 10:
            data += b"."
        header = len(data).to_bytes(4, "little", signed=True)
        self.log.debug(f'len: {len(data)}; send: {header + data!r}')
        try:
            writer.write(header + data)
            await writer.drain()
        except ConnectionError:
            self.log.debug('tcp_send: Disconnected')
            self.alive = False

    async def recv(self):
        try:
            header = await self.reader.read(4)

            int_header = 0
            for i in range(len(header)):
                int_header += header[i]

            if int_header <= 0:
                await asyncio.sleep(0.1)
                self.is_disconnected()
                if self.alive:
                    self.log.debug(f"Header: {header}")
                    await self.kick("Invalid packet - header negative")
                return b""

            if int_header > 100 * MB:
                await self.kick("Header size limit exceeded")
                self.log.warn(f"Client {self.nick}:{self.cid} sent header of >100MB - "
                              f"assuming malicious intent and disconnecting the client.")
                return b""

            data = await self.reader.read(100 * MB)
            self.log.debug(f"header: `{header}`; int_header: `{int_header}`; data: `{data}`;")

            if len(data) != int_header:
                self.log.debug(f"WARN Expected to read {int_header} bytes, instead got {len(data)}")

            abg = b"ABG:"
            if len(data) > len(abg) and data.startswith(abg):
                data = zlib.decompress(data[len(abg):])
                self.log.debug(f"ABG: {data}")
                return data
            return data
        except ConnectionError:
            self.alive = False
            return b""

    # TODO: Speed  limiter
    async def _split_load(self, start, end, d_sock, filename):
        real_size = end - start
        writer = self.down_rw[1] if d_sock else self.writer
        who = 'dwn' if d_sock else 'srv'
        if config.Server["debug"]:
            self.log.debug(f"[{who}] Real size: {real_size / MB}mb; {real_size == end}, {real_size * 2 == end}")

        with open(filename, 'rb') as f:
            f.seek(start)
            data = f.read(end)
            try:
                writer.write(data)
                await writer.drain()
                self.log.debug(f"[{who}] File sent.")
            except ConnectionError:
                self.alive = False
                self.log.debug(f"[{who}] Disconnected.")
        return real_size

    async def sync_resources(self):
        while self.alive:
            data = await self.recv()
            self.log.debug(f"data: {data!r}")
            if data.startswith(b"f"):
                file = data[1:].decode("utf-8")
                # TODO: i18n
                self.log.info(f"Requested mode: {file!r}")
                size = -1
                for mod in self.Core.mods_list:
                    if type(mod) == int:
                        continue
                    if mod.get('path') == file:
                        size = mod['size']
                        self.log.debug("File is accept.")
                        break
                self.log.debug(f"Mode size: {size}")
                if size == -1:
                    await self.tcp_send(b"CO")
                    await self.kick(f"Not allowed mod: " + file)
                    return
                await self.tcp_send(b"AG")
                t = 0
                while not self.down_rw[0]:
                    await asyncio.sleep(0.1)
                    t += 1
                    if t > 50:
                        await self.kick("Missing download socket")
                        return

                half_size = math.floor(size / 2)
                uploads = [
                    self._split_load(0, half_size, False, file),
                    self._split_load(half_size, size, True, file)
                ]
                sl0, sl1 = await asyncio.gather(*uploads)
                sent = sl0 + sl1
                ok = sent == size
                lost = size - sent
                self.log.debug(f"SplitLoad_0: {sl0}; SplitLoad_1: {sl1}; At all ({ok}): Sent: {sent}; Lost: {lost}")
                if not ok:
                    self.alive = False
                    # TODO: i18n
                    self.log.error(f"Error while sending.")
                    return
            elif data.startswith(b"SR"):
                path_list = ''
                size_list = ''
                for mod in self.Core.mods_list:
                    if type(mod) == int:
                        continue
                    path_list += f"{mod['path']};"
                    size_list += f"{mod['size']};"
                mod_list = path_list + size_list
                self.log.debug(f"Mods List: {mod_list}")
                if len(mod_list) == 0:
                    await self.tcp_send(b"-")
                else:
                    await self.tcp_send(bytes(mod_list, "utf-8"))
            elif data == b"Done":
                await self.tcp_send(b"M/levels/" + bytes(config.Game['map'], 'utf-8') + b"/info.json")
                break
        return

    async def looper(self):
        await self.tcp_send(b"P" + bytes(f"{self.cid}", "utf-8"))  # Send clientID
        await self.sync_resources()
        while self.alive:
            data = await self.recv()
            if data == b"":
                if not self.alive:
                    break
                else:
                    await asyncio.sleep(.1)
                    self.is_disconnected()
                    continue
            code = data.decode()[0]
            self.log.debug(f"Received code: {code}, data: {data}")
            match code:
                case "H":
                    # Client connected
                    self.ready = True
                    await self.tcp_send(b"Sn" + bytes(self.nick, "utf-8"), to_all=True)
                case "C":
                    # Chat
                    ev.call_event("chat_receive", f"{data}")
                    await self.tcp_send(data, to_all=True)

    async def remove_me(self):
        await asyncio.sleep(0.3)
        self.alive = False
        if (self.cid > 0 or self.nick is not None) and \
                self.Core.clients_by_nick.get(self.nick):
            # if self.ready:
            #     await self.tcp_send(b"", to_all=True)  # I'm disconnected.
            self.log.debug(f"Removing client {self.nick}:{self.cid}")
            # TODO: i18n
            self.log.info("Disconnected")
            self.Core.clients[self.cid] = None
            self.Core.clients_by_id.pop(self.cid)
            self.Core.clients_by_nick.pop(self.nick)
        else:
            self.log.debug(f"Removing client; Closing connection...")
        if not self.writer.is_closing():
            self.writer.close()
        _, down_w = self.down_rw
        if down_w and not down_w.is_closing():
            down_w.close()
