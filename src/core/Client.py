# Developed by KuiToi Dev
# File core.tcp_server.py
# Written by: SantaSpeen
# Core version: 0.4.5
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
        self._synced = False
        self._ready = False
        self._identifiers = []
        self._cars = [None] * 21  # Max 20 cars per player + 1 snowman
        self._focus_car = -1
        self._snowman = {"id": -1, "packet": ""}
        self._connect_time = 0
        self._last_position = {}

    @property
    def _writer(self):
        return self.__writer

    @property
    def alive(self):
        return self.__alive

    @property
    def log(self):
        return self._log

    @property
    def addr(self):
        return self._addr[0]

    @property
    def cid(self):
        return self._cid

    @property
    def pid(self):
        return self._cid

    @property
    def key(self):
        return self._key

    @property
    def guest(self):
        return self._guest

    @property
    def synced(self):
        return self._synced

    @property
    def ready(self):
        return self._ready

    @property
    def identifiers(self):
        return self._identifiers

    @property
    def cars(self):
        return {i: v for i, v in enumerate(self._cars) if v is not None}

    @property
    def focus_car(self):
        return self._focus_car

    @property
    def last_position(self):
        return self._last_position

    def _update_logger(self):
        self._log = utils.get_logger(f"{self.nick}:{self.cid}")
        self.log.debug(f"Update logger")

    def is_disconnected(self):
        if not self.__alive:
            return True
        if self.__writer.is_closing():
            self.log.debug(f"is_d: Disconnected.")
            self.__alive = False
            return True
        else:
            self.__alive = True
            return False

    async def kick(self, reason=None):
        if not reason:
            reason = "Kicked!"
        else:
            reason = f"{reason}"
        if not self.__alive:
            self.log.debug(f"{self.nick}.kick('{reason}') skipped: Not alive;")
            return
        self.log.info(i18n.client_kicked.format(reason))
        await self._send(f"K{reason}")
        self.__alive = False

    async def send_message(self, message, to_all=True):
        if not message:
            message = "no message"
            to_all = False
        await self._send(f"C:{message!r}", to_all=to_all)

    async def send_event(self, event_name, event_data, to_all=True):
        if isinstance(event_data, (list, tuple, dict)):
            event_data = json.dumps(event_data, separators=(',', ':'))
        else:
            event_data = f"{event_data!r}"
        if len(event_data) > 104857599:
            self.log.error("Client data too big! >=104857599")
            return
        await self._send(f"E:{event_name}:{event_data}", to_all=to_all)

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
        # self.log.debug(f'[TCP] {header + data!r}')
        try:
            writer.write(header + data)
            await writer.drain()
            return True

        except Exception as e:
            self.log.debug(f'[TCP] Disconnected: {e}')
            self.__alive = False
            await self._remove_me()
            return False

    async def _recv(self, one=False):
        while self.__alive:
            try:
                header = b""
                while len(header) < 4 and self.__alive:
                    h = await self.__reader.read(4)
                    if not h:
                        break
                    else:
                        header += h

                int_header = int.from_bytes(header, byteorder='little', signed=True)

                if int_header <= 0:
                    await asyncio.sleep(0.1)
                    self.is_disconnected()
                    if self.__alive:
                        if header == b"":
                            self.__packets_queue.append(None)
                            self.__alive = False
                            continue
                        self.log.error(f"Header: {header}")
                        await self.kick("Invalid packet - header negative")
                    self.__packets_queue.append(None)
                    continue

                if int_header > 100 * MB:
                    await self.kick("Header size limit exceeded")
                    self.log.warning("Client sent header of >100MB - "
                                     "assuming malicious intent and disconnecting the client.")
                    self.log.error(f"Last recv: {await self.__reader.read(100 * MB)}")
                    self.__packets_queue.append(None)
                    continue

                data = b""
                while len(data) < int_header and self.__alive:
                    buffer = await self.__reader.read(int_header - len(data))
                    if not buffer:
                        break
                    else:
                        data += buffer

                abg = b"ABG:"
                if len(data) > len(abg) and data.startswith(abg):
                    data = zlib.decompress(data[len(abg):])
                    # self.log.debug(f"ABG Packet: {len(data)}")

                if one:
                    return data
                self.__packets_queue.append(data)

            except ConnectionError:
                self.__alive = False
                self.__packets_queue.append(None)

    async def _split_load(self, start, end, d_sock, filename, speed_limit=None):
        real_size = end - start
        writer = self._down_sock[1] if d_sock else self.__writer
        who = 'dwn' if d_sock else 'srv'
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
                    # self.log.debug(f"[{who}] Sent {len(data)} bytes.")
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
        while self.__alive:
            data = await self._recv(True)
            if data is None:
                await self._remove_me()
                break
            if data.startswith(b"f"):
                file = data[1:].decode(config.enc)
                self.log.info(i18n.client_mod_request.format(repr(file)))
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
                tr = (time.monotonic() - t) or 0.0001
                if self.__Core.lock_upload:
                    self.__Core.lock_upload = False
                msg = i18n.client_mod_sent.format(round(size / MB, 3), math.ceil(size / tr / MB), int(tr))
                if speed:
                    msg += i18n.client_mod_sent_limit.format(int(speed * 2))
                self.log.info(msg)
                sent = sl0 + sl1
                ok = sent == size
                lost = size - sent
                self.log.debug(f"SplitLoad_0: {sl0}; SplitLoad_1: {sl1}; At all ({ok}): Sent: {sent}; Lost: {lost}")
                if not ok:
                    self.__alive = False
                    self.log.error(i18n.client_mod_sent_error.format(repr(file)))
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
                await self._send(f"M/levels/{config.Game['map']}/info.json")
                break
        return

    def _get_cid_vid(self, data: str):
        sep = data.find(":", 1) + 1
        s = data[sep:sep + 3]
        id_sep = s.find('-')
        if id_sep == -1:
            self.log.debug(
                f"Invalid packet: Could not parse pid/vid from packet, as there is no '-' separator: '{data}', {s}")
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

    async def _spawn_car(self, data):
        car_data = data[2:]
        car_id = next((i for i, car in enumerate(self._cars) if car is None), len(self._cars))
        cars_count = len(self._cars) - self._cars.count(None)
        if self._snowman['id'] != -1:
            cars_count -= 1  # -1 for unicycle
        self.log.debug(f"car_id={car_id}, cars_count={cars_count}")
        car_json = {}
        try:
            car_json = json.loads(car_data[car_data.find("{"):])
        except Exception as e:
            self.log.debug(f"Invalid car_json: Error: {e}; Data: {car_data}")
        allow = True
        allow_snowman = True
        over_spawn = False
        lua_data = ev.call_lua_event("onVehicleSpawn", self.cid, car_id, car_data[car_data.find("{"):])
        if 1 in lua_data:
            allow = False
        ev_data_list = ev.call_event("onCarSpawn", data=car_json, car_id=car_id, player=self)
        d2 = await ev.call_async_event("onCarSpawn", data=car_json, car_id=car_id, player=self)
        ev_data_list.extend(d2)
        for ev_data in ev_data_list:
            self.log.debug(ev_data)
            # TODO: handle event onCarSpawn
            pass
        pkt = f"Os:{self.roles}:{self.nick}:{self.cid}-{car_id}:{car_data}"
        snowman = car_json.get("jbm") == "unicycle"
        if allow and config.Game['max_cars'] > cars_count or (snowman and allow_snowman) or over_spawn:
            if snowman:
                unicycle_id = self._snowman['id']
                if unicycle_id != -1:
                    self.log.debug(f"Delete old unicycle: unicycle_id={unicycle_id}")
                    self._cars[unicycle_id] = None
                    await self._send(f"Od:{self.cid}-{unicycle_id}", to_all=True, to_self=True)
                self._snowman = {"id": car_id, "packet": pkt}
                self.log.debug(f"Unicycle spawn accepted: car_id={car_id}")
            else:
                self.log.debug(f"Car spawn accepted: car_id={car_id}")
            self._focus_car = car_id
            self._cars[car_id] = {
                "packet": pkt,
                "json": car_json,
                "json_ok": bool(car_json),
                "snowman": snowman,
                "over_spawn": (snowman and allow_snowman) or over_spawn,
                "pos": {}
            }
            await self._send(pkt, to_all=True, to_self=True)
        else:
            await self._send(pkt)
            des = f"Od:{self.cid}-{car_id}"
            await self._send(des)

    async def delete_car(self, car_id):
        await self._delete_car(car_id=car_id)

    async def _delete_car(self, raw_data=None, car_id=None):

        if not car_id and raw_data:
            cid, car_id = self._get_cid_vid(raw_data)
        else:
            cid = self.cid
            raw_data = f"Od:{self.cid}-{car_id}"

        if car_id != -1 and self._cars[car_id]:

            ev.call_lua_event("onVehicleDeleted", self.cid, car_id)

            admin_allow = False  # Delete from admin, for example...
            ev_data_list = ev.call_event("onCarDelete", data=self._cars[car_id], car_id=car_id, player=self)
            d2 = await ev.call_async_event("onCarDelete", data=self._cars[car_id], car_id=car_id, player=self)
            ev_data_list.extend(d2)
            for ev_data in ev_data_list:
                self.log.debug(ev_data)
                # TODO: handle event onCarDelete
                pass

            if cid == self.cid or admin_allow:
                await self._send(raw_data, to_all=True, to_self=True)
                car = self._cars[car_id]
                if car['snowman']:
                    self.log.debug(f"Snowman found")
                    unicycle_id = self._snowman['id']
                    self._snowman['id'] = -1
                    self._cars[unicycle_id] = None
                self._cars[car_id] = None
                await self._send(f"Od:{self.cid}-{car_id}", to_all=True, to_self=True)
                self.log.debug(f"Deleted car: car_id={car_id}")

        else:
            self.log.debug(f"Invalid car: car_id={car_id}")

    async def _edit_car(self, raw_data, data):
        cid, car_id = self._get_cid_vid(raw_data)
        if car_id != -1 and self._cars[car_id]:
            client = self.__Core.get_client(cid=cid)
            if client:
                car = client._cars[car_id]
                new_car_json = {}
                try:
                    new_car_json = json.loads(data[data.find("{"):])
                except Exception as e:
                    self.log.debug(f"Invalid new_car_json: Error: {e}; Data: {data}")

                allow = False
                admin_allow = False
                lua_data = ev.call_lua_event("onVehicleEdited", self.cid, car_id, data[data.find("{"):])
                if 1 in lua_data:
                    allow = False
                ev_data_list = ev.call_event("onCarEdited", data=new_car_json, car_id=car_id, player=self)
                d2 = await ev.call_async_event("onCarEdited", data=new_car_json, car_id=car_id, player=self)
                ev_data_list.extend(d2)
                for ev_data in ev_data_list:
                    self.log.debug(ev_data)
                    # TODO: handle event onCarEdited
                    pass

                if cid == self.cid or allow or admin_allow:
                    if car['snowman']:
                        unicycle_id = self._snowman['id']
                        self._snowman['id'] = -1
                        self.log.debug(f"Delete snowman")
                        await self._send(f"Od:{self.cid}-{unicycle_id}", to_all=True, to_self=True)
                        self._cars[unicycle_id] = None
                    else:
                        await self._send(raw_data, to_all=True, to_self=False)
                        if car['json_ok']:
                            old_car_json = car['json']
                            old_car_json.update(new_car_json)
                            car['json'] = old_car_json
                        self.log.debug(f"Updated car: car_id={car_id}")
        else:
            self.log.debug(f"Invalid car: car_id={car_id}")

    async def reset_car(self, car_id, x, y, z, rot=None):
        # TODO: reset_car
        self.log.debug(f"Resetting car from plugin")
        if rot is None:
            rot = {"y": 0, "w": 0, "x": 0, "z": 0}

    async def _reset_car(self, raw_data):
        cid, car_id = self._get_cid_vid(raw_data)
        if car_id != -1 and cid == self.cid and self._cars[car_id]:
            await self._send(raw_data, to_all=True, to_self=False)
            ev.call_lua_event("onVehicleReset", self.cid, car_id, raw_data[raw_data.find("{"):])
            car_json = {}
            try:
                car_json = json.loads(raw_data[raw_data.find("{"):])
            except Exception as e:
                self.log.debug(f"Invalid new_car_json: Error: {e}; Data: {raw_data}")
            ev.call_event("onCarReset", data=car_json, car_id=car_id, player=self)
            await ev.call_async_event("onCarReset", data=car_json, car_id=car_id, player=self)
            self.log.debug(f"Car reset: car_id={car_id}")
        else:
            self.log.debug(f"Invalid car: car_id={car_id}")

    async def _handle_car_codes(self, raw_data):
        if len(raw_data) < 6:
            return
        sub_code = raw_data[1]
        data = raw_data[3:]
        match sub_code:
            case "s":  # Spawn car
                self.log.debug("Trying to spawn car")
                if data[0] == "0":
                    await self._spawn_car(data)

            case "d":  # Delete car
                self.log.debug("Trying to delete car")
                await self._delete_car(raw_data)

            case "c":  # Edit car
                self.log.debug("Trying to edit car")
                await self._edit_car(raw_data, data)

            case "r":  # Reset car
                self.log.debug("Trying to reset car")
                await self._reset_car(raw_data)

            case "t":  # Broken details
                self.log.debug(f"Something changed/broken: {raw_data}")
                cid, car_id = self._get_cid_vid(raw_data)
                if car_id != -1 and cid == self.cid and self._cars[car_id]:
                    data = raw_data[raw_data.find("{"):]
                    ev.call_event("onCarChanged", car_id=car_id, data=data)
                    await ev.call_async_event("onCarChanged", car_id=car_id, data=data)
                await self._send(raw_data, to_all=True, to_self=False)

            case "m":  # Move focus car
                self.log.debug(f"Move focus to: {raw_data}")
                cid, car_id = self._get_cid_vid(raw_data[3:])
                if car_id != -1 and cid == self.cid and self._cars[car_id]:
                    self._focus_car = car_id
                    data = raw_data[raw_data.find("{"):]
                    ev.call_event("onCarFocusMove", car_id=car_id, data=data)
                    await ev.call_async_event("onCarFocusMove", car_id=car_id, data=data)
                await self._send(raw_data, to_all=True, to_self=True)

    async def _connected_handler(self):
        # Client connected
        ev.call_event("onPlayerJoin", player=self)
        await ev.call_async_event("onPlayerJoin", player=self)

        await self._send(f"Sn{self.nick}", to_all=True)  # I don't know for what it
        await self._send(f"J{i18n.game_welcome_message.format(self.nick)}", to_all=True)  # Hello message

        for client in self.__Core.clients:
            if not client:
                continue
            for car in client._cars:
                if not car:
                    continue
                await self._send(car['packet'])

        self.log.info(i18n.client_sync_time.format(round(time.monotonic() - self._connect_time, 2)))
        self._ready = True

    async def _chat_handler(self, data):
        sup = data.find(":", 2)
        if sup == -1:
            await self._send("C:Server: Invalid message.")
        msg = data[sup + 2:]
        if not msg:
            self.log.debug("Tried to send an empty event, ignoring")
            return
        to_ev = {"message": msg, "player": self}
        lua_data = ev.call_lua_event("onChatMessage", self.cid, self.nick, msg)
        if 1 in lua_data:
            if config.Options['log_chat']:
                self.log.info(f"{self.nick}: {msg}")
            return
        ev_data_list = ev.call_event("onChatReceive", **to_ev)
        d2 = await ev.call_async_event("onChatReceive", **to_ev)
        ev_data_list.extend(d2)
        need_send = True
        for ev_data in ev_data_list:
            if ev_data is None:
                continue
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
                if config.Options['log_chat']:
                    self.log.info(f"{message}" if to_all else f"{self.nick}: {msg}")
                await self._send(f"C:{message}", to_all=to_all, to_self=to_self, writer=writer)
                need_send = False
            except KeyError:
                self.log.error(i18n.client_event_invalid_data.format(ev_data))
            except AttributeError:
                self.log.error(i18n.client_event_invalid_data.format(ev_data))
        if need_send:
            if config.Options['log_chat']:
                self.log.info(f"{self.nick}: {msg}")
            await self._send(data, to_all=True)

    async def _handle_codes(self, data):
        if not data:
            self.__alive = False
            return

        # Codes: V W X Y
        if 89 >= data[0] >= 86:
            await self._send(data, to_all=True, to_self=False)
            return

        _bytes = False
        try:
            data = data.decode()
        except UnicodeDecodeError:
            _bytes = True
            self.log.error(f"UnicodeDecodeError: {data}")
            self.log.info("Some things are skipping...")

        # Codes: p, Z in udp_server.py
        match data[0]:  # At data[0] code
            case "H":  # Map load, client ready
                await self._connected_handler()

            case "C":  # Chat handler
                if _bytes:
                    return
                await self._chat_handler(data)

            case "O":  # Cars handler
                if _bytes:
                    return
                await self._handle_car_codes(data)

            case "E":  # Client events handler
                if len(data) < 2:
                    self.log.debug("Tried to send an empty event, ignoring.")
                    return
                if _bytes:
                    sep = data.find(b":", 2)
                    self.log.warning("Bytes event!")
                else:
                    sep = data.find(":", 2)
                if sep == -1:
                    self.log.error(f"Received event in invalid format (missing ':'), got: {data}")
                event_name = data[2:sep]
                even_data = data[sep + 1:]
                ev.call_lua_event(event_name, even_data)
                ev.call_event(event_name, data=even_data, player=self)
                await ev.call_async_event(event_name, data=even_data, player=self)
            case "N":
                await self._send(data, to_all=True, to_self=False)

    async def _looper(self):
        ev.call_lua_event("onPlayerConnecting", self.cid)
        self._connect_time = time.monotonic()
        await self._send(f"P{self.cid}")  # Send clientID
        await self._sync_resources()
        ev.call_lua_event("onPlayerJoining", self.cid)
        tasks = self.__tasks
        recv = asyncio.create_task(self._recv())
        tasks.append(recv)
        self._synced = True
        while self.__alive:
            if len(self.__packets_queue) > 0:
                for index, packet in enumerate(self.__packets_queue):
                    # self.log.debug(f"Packet: {packet}")
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
            for i, car in enumerate(self._cars):
                if not car:
                    continue
                self.log.debug(f"Removing car: car_id={i}")
                await self._send(f"Od:{self.cid}-{i}", to_all=True, to_self=False)
            if self.ready:
                await self._send(f"J{self.nick} disconnected!", to_all=True, to_self=False)  # I'm disconnected.
            self.log.debug(f"Removing client")
            ev.call_lua_event("onPlayerDisconnect", self.cid)
            ev.call_event("onPlayerDisconnect", player=self)
            await ev.call_async_event("onPlayerDisconnect", player=self)

            self.log.info(
                i18n.client_player_disconnected.format(
                    round((time.monotonic() - self._connect_time) / 60, 2)
                )
            )
            self.__Core.clients[self.cid] = None
            del self.__Core.clients_by_id[self.cid]
            del self.__Core.clients_by_nick[self.nick]
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
