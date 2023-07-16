# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Core version: 0.2.3
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import json
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
        self.nick = None
        self.roles = None
        self._guest = True
        self._ready = False
        self._cars = []

    @property
    def _writer(self):
        return self.__writer

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
    def guest(self):
        return self._guest

    @property
    def ready(self):
        return self._ready

    @property
    def cars(self):
        return self._cars

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
            self.log.debug(f"{self.nick}.kick('{reason}') skipped: Not alive;")
            return
        # TODO: i18n
        self.log.info(f"Kicked with reason: \"{reason}\"")
        await self._send(b"K" + bytes(reason, "utf-8"))
        self.__alive = False

    async def _send(self, data, to_all=False, to_self=True, to_udp=False, writer=None):

        # TNetwork.cpp; Line: 383
        # BeamMP TCP protocol sends a header of 4 bytes, followed by the data.
        # [][][][][][]...[]
        # ^------^^---...-^
        #  size     data

        if type(data) == str:
            data = bytes(data, "utf-8")

        if writer is None:
            writer = self.__writer

        if to_all:
            code = chr(data[0])
            for client in self.__Core.clients:
                if not client or (client is self and not to_self):
                    continue
                if not to_udp or code in ['V', 'W', 'Y', 'E']:
                    if code in ['O', 'T'] or len(data) > 1000:
                        # TODO: Compress data
                        await client._send(data)
                    else:
                        await client._send(data)
                else:
                    # TODO: UDP send
                    self.log.debug(f"UDP Part not ready: {code}")
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
                self.log.warning(f"Client {self.nick}:{self.cid} sent header of >100MB - "
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
                    await self._send(b"CO")
                    await self.kick(f"Not allowed mod: " + file)
                    return
                await self._send(b"AG")
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
                    await self._send(b"-")
                else:
                    await self._send(bytes(mod_list, "utf-8"))
            elif data == b"Done":
                await self._send(b"M/levels/" + bytes(config.Game['map'], 'utf-8') + b"/info.json")
                break
        return

    async def _looper(self):
        await self._send(b"P" + bytes(f"{self.cid}", "utf-8"))  # Send clientID
        await self._sync_resources()
        while self.__alive:
            data = await self._recv()
            if not data:
                self.__alive = False
                break

            # Codes: V W X Y
            if 89 >= data[0] >= 86:
                await self._send(data, to_all=True, to_self=False)

            data = data.decode('utf-8')

            code = data[0]
            self.log.debug(f"Received code: {code}, data: {data}")
            match code:
                case "H":
                    # Client connected

                    ev.call_event("onPlayerJoin", player=self)
                    await ev.call_async_event("onPlayerJoin", player=self)

                    await self._send(f"Sn{self.nick}", to_all=True)  # I don't know for what it
                    await self._send(f"JWelcome {self.nick}!", to_all=True)  # Hello message
                    self._ready = True

                    for client in self.__Core.clients:
                        if not client:
                            continue
                        for car in client.cars:
                            await self._send(car)

                case "C":  # Chat handler
                    msg = data[4 + len(self.nick):]
                    if not msg:
                        self.log.debug("Tried to send an empty event, ignoring")
                        continue
                    self.log.info(f"Received message: {msg}")
                    to_ev = {"message": msg, "player": self}
                    ev_data_list = ev.call_event("onChatReceive", **to_ev)
                    d2 = await ev.call_async_event("onChatReceive", **to_ev)
                    ev_data_list.extend(d2)
                    need_send = True
                    for ev_data in ev_data_list:
                        try:
                            message = ev_data["message"]
                            to_all = ev_data.get("to_all")
                            if to_all is None:
                                if need_send:
                                    need_send = False
                                to_all = True
                            if to_all:
                                if need_send:
                                    need_send = False
                            to_self = ev_data.get("to_self")
                            if to_self is None:
                                to_self = True
                            to_client = ev_data.get("to_client")
                            writer = None
                            if to_client:
                                writer = to_client._writer
                            await self._send(f"C:{message}", to_all=to_all, to_self=to_self, writer=writer)
                        except KeyError | AttributeError:
                            self.log.error(f"Returns invalid data: {ev_data}")
                    if need_send:
                        await self._send(data, to_all=True)

                case "O":  # Vehicle info handler
                    if len(data) < 6:
                        continue
                    sub_code = data[1]
                    data = data[3:]
                    vid = -1
                    pid = -1
                    match sub_code:
                        case "s":  # Spawn car
                            if data[0] == "0":
                                car_id = len(self._cars)
                                self.log.debug(f"Created a car with ID {car_id}")
                                car_data = data[2:]
                                car_json = {}
                                try:
                                    car_json = json.loads(data[5:])
                                except Exception as e:
                                    self.log.debug(f"Invalid car_json: Error: {e}; Data: {car_data}")
                                # TODO: Call event onVehicleSpawn

                                spawn = True
                                pkt = f"Os:{self.roles}:{self.nick}:{self.cid}-{car_id}:{car_data}"
                                if spawn and (config.Game['max_cars'] > car_id or car_json.get("jbm") == "unicycle"):
                                    self.log.debug(f"Car spawn accepted.")
                                    self._cars.append(car_data)
                                    await self._send(pkt, to_all=True)
                                else:
                                    await self._send(pkt)
                                    des = f"Od:{self.cid}-{car_id}"
                                    await self._send(des)
                        case "c":  # Edit car
                            # TODO: edit car
                            pass
                        case "d":  # Delete car
                            # TODO: delete car
                            pass
                        case "r":  # Reset car
                            # TODO: reset car
                            pass
                        case "t" | "m":
                            pass

                case "E":  # Client events handler
                    # TODO: HandleEvent
                    pass

                case "N":
                    # TODO: N
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
