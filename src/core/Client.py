# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Core version: 0.4.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import json
import math
import time
import zlib

from core import utils


class Client:

    def __init__(self, reader, writer, core):
        self.__reader = reader
        self.__writer = writer
        self.__Core = core
        self.__alive = True
        self.__packets_queue = []
        self.__tasks = []
        self._down_sock = (None, None)
        self._udp_sock = (None, None)
        self._loop = asyncio.get_event_loop()
        self._log = utils.get_logger("player(None:0)")
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
        await self._send(f"K{reason}")
        self.__alive = False

    async def send_message(self, message, to_all=True):
        pass

    async def send_event(self, event_name, event_data):
        pass

    async def _send(self, data, to_all=False, to_self=True, to_udp=False, writer=None):

        # TNetwork.cpp; Line: 383
        # BeamMP TCP protocol sends a header of 4 bytes, followed by the data.
        # [][][][][][]...[]
        # ^------^^---...-^
        #  size     data

        if type(data) == str:
            data = bytes(data, config.enc)

        if to_all:
            code = chr(data[0])
            for client in self.__Core.clients:
                if not client or (client is self and not to_self):
                    continue
                if not to_udp or code in ['V', 'W', 'Y', 'E']:
                    await client._send(data)
                else:
                    await client._send(data, to_udp=to_udp)
            return

        if not self.__alive:
            return False

        if writer is None:
            writer = self.__writer

        if len(data) > 400:
            data = b"ABG:" + zlib.compress(data, level=zlib.Z_BEST_COMPRESSION)

        if to_udp:
            udp_sock = self._udp_sock[0]
            udp_addr = self._udp_sock[1]
            # self.log.debug(f'[UDP] len: {len(data)}; send: {data!r}')
            if udp_sock and udp_addr:
                try:
                    if not udp_sock.is_closing():
                        # self.log.debug(f'[UDP] {data!r}')
                        udp_sock.sendto(data, udp_addr)
                except OSError:
                    self.log.debug("[UDP] Error sending")
                except Exception as e:
                    self.log.debug(f"[UDP] Error sending: {e}")
                    self.log.exception(e)
            return

        header = len(data).to_bytes(4, "little", signed=True)
        self.log.debug(f'[TCP] {header + data!r}')
        try:
            writer.write(header + data)
            await writer.drain()
            return True

        except ConnectionError:
            self.log.debug('[TCP] Disconnected')
            self.__alive = False
            await self._remove_me()
            return False

    # async def __handle_packet(self, data, int_header):
    #     self.log.debug(f"int_header: {int_header}; data: {data};")
    #     if len(data) != int_header:
    #         self.log.debug(f"WARN Expected to read {int_header} bytes, instead got {len(data)}")
    #
    #         recv2 = data[int_header:]
    #         header2 = recv2[:4]
    #         data2 = recv2[4:]
    #         int_header2 = int.from_bytes(header2, byteorder='little', signed=True)
    #         t = asyncio.create_task(self.__handle_packet(data2, int_header2))
    #         self.__tasks.append(t)
    #         data = data[:4 + int_header]
    #
    #     abg = b"ABG:"
    #     if len(data) > len(abg) and data.startswith(abg):
    #         data = zlib.decompress(data[len(abg):])
    #         self.log.debug(f"ABG Packet: {len(data)}")
    #
    #     self.__packets_queue.append(data)
    #     self.log.debug(f"Packets in queue: {len(self.__packets_queue)}")

    async def _recv(self, one=False):
        while self.__alive:
            try:
                header = await self.__reader.read(4)

                int_header = int.from_bytes(header, byteorder='little', signed=True)

                if int_header <= 0:
                    await asyncio.sleep(0.1)
                    self.is_disconnected()
                    if self.__alive:
                        if header == b"":
                            self.__packets_queue.append(None)
                            self.__alive = False
                            continue
                        self.log.debug(f"Header: {header}")
                        await self.kick("Invalid packet - header negative")
                    self.__packets_queue.append(None)
                    continue

                if int_header > 100 * MB:
                    await self.kick("Header size limit exceeded")
                    self.log.warning("Client sent header of >100MB - "
                                     "assuming malicious intent and disconnecting the client.")
                    self.__packets_queue.append(None)
                    self.log.error(f"Last recv: {await self.__reader.read(100 * MB)}")
                    continue

                data = await self.__reader.read(int_header)

                self.log.debug(f"int_header: {int_header}; data: `{data}`;")
                abg = b"ABG:"
                if len(data) > len(abg) and data.startswith(abg):
                    data = zlib.decompress(data[len(abg):])
                    self.log.debug(f"ABG Packet: {len(data)}")

                if one:
                    # self.log.debug(f"int_header: `{int_header}`; data: `{data}`;")
                    return data
                # FIXME
                # else:
                #     t = asyncio.create_task(self.__handle_packet(data, int_header))
                #     self.__tasks.append(t)
                self.__packets_queue.append(data)

            except ConnectionError:
                self.__alive = False
                self.__packets_queue.append(None)

    async def _split_load(self, start, end, d_sock, filename, speed_limit=None):
        real_size = end - start
        writer = self._down_sock[1] if d_sock else self.__writer
        who = 'dwn' if d_sock else 'srv'
        if config.Server["debug"]:
            self.log.debug(f"[{who}] Real size: {real_size / MB}mb; {real_size == end}, {real_size * 2 == end}")

        with open(filename, 'rb') as f:
            f.seek(start)
            total_sent = 0
            start_time = time.monotonic()
            while total_sent < real_size:
                data = f.read(min(MB, real_size - total_sent))  # read data in chunks of 1MB or less
                try:
                    writer.write(data)
                    await writer.drain()
                    self.log.debug(f"[{who}] Sent {len(data)} bytes.")
                except ConnectionError:
                    self.__alive = False
                    self.log.debug(f"[{who}] Disconnected.")
                    break
                total_sent += len(data)

                # Calculate delay based on speed limit
                if speed_limit:
                    elapsed_time = time.monotonic() - start_time
                    expected_time = total_sent / (speed_limit * MB)
                    if expected_time > elapsed_time:
                        await asyncio.sleep(expected_time - elapsed_time)

        return total_sent

    async def _sync_resources(self):
        tsr = time.monotonic()
        while self.__alive:
            data = await self._recv(True)
            if data.startswith(b"f"):
                file = data[1:].decode(config.enc)
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
                while not self._down_sock[0]:
                    await asyncio.sleep(0.1)
                    t += 1
                    if t > 50:
                        await self.kick("Missing download socket")
                        return
                if config.Options['use_queue']:
                    while self.__Core.lock_upload:
                        await asyncio.sleep(.2)
                    self.__Core.lock_upload = True
                speed = config.Options["speed_limit"]
                if speed:
                    speed = speed / 2
                half_size = math.floor(size / 2)
                t = time.monotonic()
                uploads = [
                    self._split_load(0, half_size, False, file, speed),
                    self._split_load(half_size, size, True, file, speed)
                ]
                sl0, sl1 = await asyncio.gather(*uploads)
                tr = time.monotonic() - t
                if self.__Core.lock_upload:
                    self.__Core.lock_upload = False
                # TODO: i18n
                msg = f"Mod sent: Size {round(size / MB, 3)}mb Speed {int(size / tr / MB)}Mb/s ({int(tr)}s)"
                if speed:
                    msg += f" of limit {int(speed * 2)}Mb/s"
                self.log.info(msg)
                sent = sl0 + sl1
                ok = sent == size
                lost = size - sent
                self.log.debug(f"SplitLoad_0: {sl0}; SplitLoad_1: {sl1}; At all ({ok}): Sent: {sent}; Lost: {lost}")
                if not ok:
                    self.__alive = False
                    # TODO: i18n
                    self.log.error(f"Error while sending: {file!r}")
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
                    await self._send(mod_list)
            elif data == b"Done":
                for c in range(int(config.Game['max_cars'] * 2.3)):
                    self._cars.append(None)
                await self._send(f"M/levels/{config.Game['map']}/info.json")
                self.log.info(f"Syncing time: {time.monotonic() - tsr}")
                break
        return

    def _get_cid_vid(self, data: str):
        sep = data.find(":", 1) + 1
        s = data[sep:sep + 3]
        id_sep = s.find('-')
        if id_sep == -1:
            self.log.debug(
                f"Invalid packet: Could not parse pid/vid from packet, as there is no '-' separator: '{data}'")
            return -1, -1
        cid = s[:id_sep]
        vid = s[id_sep + 1:]
        if cid.isdigit() and vid.isdigit():
            try:
                cid = int(cid)
                vid = int(vid)
                return cid, vid
            except ValueError:
                self.log.debug(f"Invalid packet: Could not parse cid/vid from packet, as one or both are not valid "
                               f"numbers: '{s}'")
                return -1, -1
        self.log.debug(f"Invalid packet: Could not parse pid/vid from packet: '{data}'")
        return -1, -1

    async def _handle_car_codes(self, dta):
        if len(dta) < 6:
            return
        sub_code = dta[1]
        data = dta[3:]
        match sub_code:
            case "s":  # Spawn car
                self.log.debug("Trying to spawn car")
                if data[0] == "0":
                    car_id = 0
                    for c in self.cars:
                        if c is None:
                            break
                        car_id += 1
                    self.log.debug(f"Created a car: car_id={car_id}")
                    car_data = data[2:]
                    car_json = {}
                    try:
                        car_json = json.loads(data[data.find("{"):])
                    except Exception as e:
                        self.log.debug(f"Invalid car_json: Error: {e}; Data: {car_data}")
                    # allow = True
                    over_spawn = False
                    # TODO: Call event onCarSpawn
                    pkt = f"Os:{self.roles}:{self.nick}:{self.cid}-{car_id}:{car_data}"
                    unicycle = car_json.get("jbm") == "unicycle"
                    # FIXME: unicycle
                    # if (allow and (config.Game['max_cars'] > car_id or unicycle)) or over_spawn:
                    if config.Game['max_cars'] > car_id and not unicycle:
                        self.log.debug(f"Car spawn accepted.")
                        self._cars[car_id] = {
                            "packet": pkt,
                            "json": car_json,
                            "json_ok": bool(car_json),
                            "unicycle": unicycle,
                            "over_spawn": over_spawn or unicycle
                        }
                        await self._send(pkt, to_all=True, to_self=True)
                    else:
                        await self._send(pkt)
                        des = f"Od:{self.cid}-{car_id}"
                        await self._send(des)
            case "d":  # Delete car
                self.log.debug("Trying to delete car")
                cid, car_id = self._get_cid_vid(dta)
                if car_id != -1 and cid == self.cid:
                    # TODO: Call event onCarDelete
                    await self._send(dta, to_all=True, to_self=True)
                    try:
                        car = self.cars[car_id]
                        if car['unicycle']:
                            self._cars.pop(car_id)
                        else:
                            self._cars[car_id] = None
                        await self._send(f"Od:{self.cid}-{car_id}")
                        self.log.debug(f"Deleted car: car_id={car_id}")
                    except IndexError:
                        self.log.debug(f"Unknown car: car_id={car_id}")
            case "c":  # Edit car
                self.log.debug("Trying to edit car")
                allow = True
                # TODO: Call event onCarEdited
                cid, car_id = self._get_cid_vid(dta)
                if car_id != -1 and cid == self.cid:
                    try:
                        car = self.cars[car_id]
                        if car['unicycle']:
                            self._cars.pop(car_id)
                            await self._send(f"Od:{self.cid}-{car_id}", to_all=True, to_self=True)
                        elif allow:
                            await self._send(dta, to_all=True, to_self=False)
                            if car['json_ok']:
                                old_car_json = car['json']
                                try:
                                    new_car_json = json.loads(data[data.find("{"):])
                                    old_car_json.update(new_car_json)
                                    car['json'] = new_car_json
                                    self.log.debug(f"Updated car: car_id={car_id}")
                                except Exception as e:
                                    self.log.debug(f"Invalid new_car_json: Error: {e}; Data: {data}")

                    except IndexError:
                        self.log.debug(f"Unknown car: car_id={car_id}")
            case "r":  # Reset car
                self.log.debug("Trying to reset car")
                cid, car_id = self._get_cid_vid(dta)
                if car_id != -1 and cid == self.cid:
                    # TODO: Call event onCarReset
                    await self._send(dta, to_all=True, to_self=False)
                    self.log.debug(f"Car reset: car_id={car_id}")
            case "t":
                self.log.debug(f"Received 'Ot' packet: {dta}")
                await self._send(dta, to_all=True, to_self=False)
            case "m":
                await self._send(dta, to_all=True, to_self=True)

    async def _handle_codes(self, data):
        if not data:
            self.__alive = False
            return

        # Codes: V W X Y
        if 89 >= data[0] >= 86:
            await self._send(data, to_all=True, to_self=False)
        try:
            data = data.decode()
        except UnicodeDecodeError:
            self.log.debug(f"UnicodeDecodeError: {data}")
            return

        code = data[0]
        # Codes: p, Z in udp_server.py
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
                        if not car:
                            continue
                        await self._send(car['packet'])

            case "C":  # Chat handler
                sup = data.find(":", 2)
                if sup == -1:
                    await self._send("C:Server: Invalid message.")
                msg = data[sup + 2:]
                if not msg:
                    self.log.debug("Tried to send an empty event, ignoring")
                    return
                self.log.info(f"{self.nick}: {msg}")
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
                            to_all = True
                        to_self = ev_data.get("to_self")
                        if to_self is None:
                            to_self = True
                        to_client = ev_data.get("to_client")
                        writer = None
                        if to_client:
                            # noinspection PyProtectedMember
                            writer = to_client._writer
                        await self._send(f"C:{message}", to_all=to_all, to_self=to_self, writer=writer)
                        need_send = False
                    except KeyError | AttributeError:
                        self.log.error(f"Returns invalid data: {ev_data}")
                if need_send:
                    await self._send(data, to_all=True)

            case "O":  # Cars handler
                await self._handle_car_codes(data)

            case "E":  # Client events handler
                # TODO: HandleEvent
                pass

            case "N":
                await self._send(data, to_all=True, to_self=False)

    async def _looper(self):
        await self._send(f"P{self.cid}")  # Send clientID
        await self._sync_resources()
        tasks = self.__tasks
        recv = asyncio.create_task(self._recv())
        tasks.append(recv)
        while self.__alive:
            if len(self.__packets_queue) > 0:
                for index, packet in enumerate(self.__packets_queue):
                    self.log.debug(f"Packet: {packet}")
                    del self.__packets_queue[index]
                    task = self._loop.create_task(self._handle_codes(packet))
                    tasks.append(task)
            else:
                await asyncio.sleep(0.1)
        await asyncio.gather(*tasks)

    async def _remove_me(self):
        await asyncio.sleep(0.3)
        self.__alive = False
        if (self.cid > 0 or self.nick is not None) and \
                self.__Core.clients_by_nick.get(self.nick):
            for i, car in enumerate(self.cars):
                if not car:
                    continue
                self.log.debug(f"Removing car: car_id={i}")
                await self._send(f"Od:{self.cid}-{i}", to_all=True, to_self=False)
            if self.ready:
                await self._send(f"J{self.nick} disconnected!", to_all=True, to_self=False)  # I'm disconnected.
            self.log.debug(f"Removing client")
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
            _, down_w = self._down_sock
            if down_w and not down_w.is_closing():
                down_w.close()
        except Exception as e:
            self.log.debug(f"Error while closing download writer: {e}")
