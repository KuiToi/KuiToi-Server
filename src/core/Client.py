import asyncio
import math
import zlib

from core import utils


class Client:

    def __init__(self, reader, writer, core):
        self.__reader = reader
        self.__writer = writer
        self._down_rw = (None, None)
        self.__Core = core
        self.__alive = True
        self._loop = asyncio.get_event_loop()
        self._log = utils.get_logger("client(None:0)")
        self._addr = writer.get_extra_info("sockname")
        self._cid = -1
        self._key = None
        self._nick = None
        self._roles = None
        self._guest = True
        self._ready = False
        self._cars = []

    @property
    def log(self):
        return self._log

    @property
    def addr(self):
        return self._addr

    @property
    def cid(self):
        return self._cid

    @property
    def key(self):
        return self._key

    @property
    def nick(self):
        return self._nick

    @property
    def roles(self):
        return self._roles

    @property
    def guest(self):
        return self._guest

    @property
    def ready(self):
        return self._ready

    @property
    def cars(self):
        return self.cars

    def _update_logger(self):
        self._log = utils.get_logger(f"{self.nick}:{self.cid}")
        self.log.debug(f"Update logger")

    def is_disconnected(self):
        if not self.__alive:
            return True
        res = self.__writer.is_closing()
        if res:
            self.log.debug(f"Disconnected.")
            self.__alive = False
            return True
        else:
            self.log.debug(f"Alive.")
            self.__alive = True
            return False

    async def kick(self, reason):
        if not self.__alive:
            self.log.debug(f"Kick({reason}) skipped;")
            return
        # TODO: i18n
        self.log.info(f"Kicked with reason: \"{reason}\"")
        await self._tcp_send(b"K" + bytes(reason, "utf-8"))
        self.__alive = False

    async def _tcp_send(self, data, to_all=False, to_self=True, to_udp=False, writer=None):

        # TNetwork.cpp; Line: 383
        # BeamMP TCP protocol sends a header of 4 bytes, followed by the data.
        # [][][][][][]...[]
        # ^------^^---...-^
        #  size     data

        if writer is None:
            writer = self.__writer

        if to_all:
            code = data[:1]
            for client in self.__Core.clients:
                if not client or (client == self and not to_self):
                    continue
                if not to_udp or code in [b'W', b'Y', b'V', b'E']:
                    if code in [b'O', b'T'] or len(data) > 1000:
                        # TODO: Compress data
                        await client._tcp_send(data)
                    else:
                        await client._tcp_send(data)
                else:
                    # TODO: UDP send
                    pass
            return

        header = len(data).to_bytes(4, "little", signed=True)
        self.log.debug(f'len: {len(data)}; send: {header + data!r}')
        try:
            writer.write(header + data)
            await writer.drain()
        except ConnectionError:
            self.log.debug('tcp_send: Disconnected')
            self.__alive = False

    async def _recv(self):
        try:
            header = await self.__reader.read(4)

            int_header = 0
            for i in range(len(header)):
                int_header += header[i]

            if int_header <= 0:
                await asyncio.sleep(0.1)
                self.is_disconnected()
                if self.__alive:
                    self.log.debug(f"Header: {header}")
                    await self.kick("Invalid packet - header negative")
                return b""

            if int_header > 100 * MB:
                await self.kick("Header size limit exceeded")
                self.log.warn(f"Client {self.nick}:{self.cid} sent header of >100MB - "
                              f"assuming malicious intent and disconnecting the client.")
                return b""

            data = await self.__reader.read(100 * MB)
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
            self.__alive = False
            return b""

    async def _split_load(self, start, end, d_sock, filename):
        # TODO: Speed  limiter
        real_size = end - start
        writer = self._down_rw[1] if d_sock else self.__writer
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
                self.__alive = False
                self.log.debug(f"[{who}] Disconnected.")
        return real_size

    async def _sync_resources(self):
        while self.__alive:
            data = await self._recv()
            self.log.debug(f"data: {data!r}")
            if data.startswith(b"f"):
                file = data[1:].decode("utf-8")
                # TODO: i18n
                self.log.info(f"Requested mode: {file!r}")
                size = -1
                for mod in self.__Core.mods_list:
                    if type(mod) == int:
                        continue
                    if mod.get('path') == file:
                        size = mod['size']
                        self.log.debug("File is accept.")
                        break
                self.log.debug(f"Mode size: {size}")
                if size == -1:
                    await self._tcp_send(b"CO")
                    await self.kick(f"Not allowed mod: " + file)
                    return
                await self._tcp_send(b"AG")
                t = 0
                while not self._down_rw[0]:
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
                    self.__alive = False
                    # TODO: i18n
                    self.log.error(f"Error while sending.")
                    return
            elif data.startswith(b"SR"):
                path_list = ''
                size_list = ''
                for mod in self.__Core.mods_list:
                    if type(mod) == int:
                        continue
                    path_list += f"{mod['path']};"
                    size_list += f"{mod['size']};"
                mod_list = path_list + size_list
                self.log.debug(f"Mods List: {mod_list}")
                if len(mod_list) == 0:
                    await self._tcp_send(b"-")
                else:
                    await self._tcp_send(bytes(mod_list, "utf-8"))
            elif data == b"Done":
                await self._tcp_send(b"M/levels/" + bytes(config.Game['map'], 'utf-8') + b"/info.json")
                break
        return

    async def _looper(self):
        await self._tcp_send(b"P" + bytes(f"{self.cid}", "utf-8"))  # Send clientID
        await self._sync_resources()
        # TODO: GlobalParser
        while self.__alive:
            data = await self._recv()
            if not data:
                self.__alive = False
                break

            if 89 >= data[0] >= 86:
                # TODO: Network.SendToAll
                pass

            code = data.decode()[0]
            self.log.debug(f"Received code: {code}, data: {data}")
            match code:
                case "H":
                    # Client connected
                    self._ready = True

                    ev.call_event("player_join", self)
                    await ev.call_async_event("player_join", self)

                    bnick = bytes(self.nick, "utf-8")
                    await self._tcp_send(b"Sn" + bnick, to_all=True)  # I don't know for what it
                    await self._tcp_send(b"JWelcome" + bnick + b"!", to_all=True)  # Hello message

                    # TODO: Sync cars
                    # for client in self.__Core.clients:
                    #     for car in client.cars:
                    #         await self._tcp_send(car)

                case "C":
                    # Chat
                    msg = data[2:].decode()
                    if not msg:
                        self.log.debug("Tried to send an empty event, ignoring")
                        continue
                    self.log.info(f"Received message: {msg}")
                    # TODO: Handle chat event
                    ev_data = ev.call_event("chat_receive", msg)
                    d2 = await ev.call_async_event("chat_receive", msg)
                    ev_data.extend(d2)
                    self.log.info(f"TODO: Handle chat event; {ev_data}")
                    await self._tcp_send(data, to_all=True)

                case "O":
                    # TODO: ParseVehicle
                    pass

                case "E":
                    # TODO: HandleEvent
                    pass

                case "N":
                    # TODO: N
                    pass

                case _:
                    pass

    async def _remove_me(self):
        await asyncio.sleep(0.3)
        self.__alive = False
        if (self.cid > 0 or self.nick is not None) and \
                self.__Core.clients_by_nick.get(self.nick):
            # if self.ready:
            #     await self.tcp_send(b"", to_all=True)  # I'm disconnected.
            self.log.debug(f"Removing client {self.nick}:{self.cid}")
            # TODO: i18n
            self.log.info("Disconnected")
            self.__Core.clients[self.cid] = None
            self.__Core.clients_by_id.pop(self.cid)
            self.__Core.clients_by_nick.pop(self.nick)
        else:
            self.log.debug(f"Removing client; Closing connection...")
        try:
            if not self.__writer.is_closing():
                self.__writer.close()
        except Exception as e:
            self.log.debug(f"Error while closing writer: {e}")
        try:
            _, down_w = self._down_rw
            if down_w and not down_w.is_closing():
                down_w.close()
        except Exception as e:
            self.log.debug(f"Error while closing download writer: {e}")
