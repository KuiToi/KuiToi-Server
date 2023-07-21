import asyncio
import os
import platform
import random
import shutil

from lupa.lua53 import LuaRuntime

from core import get_logger


# noinspection PyPep8Naming
class MP:

    # In ./in_lua.lua
    # MP.CreateTimer
    # MP.Sleep

    def __init__(self, name: str, lua: LuaRuntime):
        self.loop = asyncio.get_event_loop()
        self.log = get_logger(f"LuaPlugin | {name}")
        self.name = name
        self.tasks = []
        self._lua = lua
        self._local_events = {
            "onInit": [], "onShutdown": [], "onPlayerAuth": [], "onPlayerConnecting": [], "onPlayerJoining": [],
            "onPlayerJoin": [], "onPlayerDisconnect": [], "onChatMessage": [], "onVehicleSpawn": [],
            "onVehicleEdited": [], "onVehicleDeleted": [], "onVehicleReset": [], "onFileChanged": []
        }

    def _print(self, *args):
        s = " ".join(map(str, args))
        self.log.info(s)

    def GetOSName(self) -> str:
        self.log.debug("request MP.GetOSName()")
        pl = platform.system()
        if pl in ["Linux", "Windows"]:
            return pl
        return "Other"

    def GetServerVersion(self) -> tuple[int, int, int]:
        self.log.debug("request MP.GetServerVersion()")
        return ev.call_event("_get_BeamMP_version")[0]

    def RegisterEvent(self, event_name: str, function_name: str) -> None:
        self.log.debug("request MP.RegisterEvent()")
        event_func = self._lua.globals()[function_name]
        ev.register_event(event_name, event_func, lua=True)
        if event_name not in self._local_events:
            self._local_events.update({str(event_name): [event_func]})
        else:
            self._local_events[event_name].append(event_func)
        self.log.debug("Register ok (local)")

    def CreateEventTimer(self, event_name: str, interval_ms: int, strategy: int = None):
        self.log.debug("request CreateEventTimer()")
        # TODO: CreateEventTimer

    def CancelEventTimer(self, event_name: str):
        self.log.debug("request CancelEventTimer()")
        # TODO: CancelEventTimer

    def TriggerLocalEvent(self, event_name, *args):
        self.log.debug("request TriggerLocalEvent()")
        self.log.debug(f"Calling lcoal lua event: '{event_name}'")
        funcs_data = []
        if event_name in self._local_events.keys():
            for func in self._local_events[event_name]:
                try:
                    funcs_data.append(func(*args))
                except Exception as e:
                    self.log.error(f'Error while calling "{event_name}"; In function: "{func.__name__}"')
                    self.log.exception(e)
        else:
            self.log.warning(f"Event {event_name} does not exist, maybe ev.call_lua_event() or MP.Trigger<>Event()?. "
                             f"Just skipping it...")

        return self._lua.table_from({i: v for i, v in enumerate(funcs_data)})

    def TriggerGlobalEvent(self, event_name, *args):
        self.log.debug("request TriggerGlobalEvent()")
        return self._lua.table(
            IsDone=lambda: True,
            GetResults=lambda: self._lua.table_from({i: v for i, v in enumerate(ev.call_lua_event(event_name, *args))})
        )

    def SendChatMessage(self, player_id, message):
        self.log.debug("request SendChatMessage()")
        client = ev.call_event("_get_player", cid=player_id)[0]
        to_all = False
        if player_id < 0:
            to_all = True
            client = client[0]
        if client and message:
            t = self.loop.create_task(client.send_message(f"Server: {message}", to_all=to_all))
            self.tasks.append(t)

    def TriggerClientEvent(self, player_id, event_name, data):
        self.log.debug("request TriggerClientEvent()")
        client = ev.call_event("_get_player", cid=player_id)[0]
        to_all = False
        if player_id < 0:
            to_all = True
            client = client[0]
        if client and event_name and data:
            t = self.loop.create_task(client.send_event(event_name, data, to_all=to_all))
            self.tasks.append(t)
            return True, None
        elif not client:
            return False, "Client expired"
        else:
            return False, "Can't found event_name or data"

    def TriggerClientEventJson(self, player_id, event_name, data):
        # TODO: TriggerClientEventJson
        self.log.debug("request TriggerClientEventJson()")
        print(list(data.values()))
        print(list(data.items()))

    def GetPlayerCount(self):
        self.log.debug("request GetPlayerCount()")
        return len(ev.call_event("_get_player", cid=-1)[0])

    def GetPositionRaw(self, player_id, car_id):
        self.log.debug("request GetPositionRaw()")
        if player_id < 0:
            return self._lua.table(), "Bad client"
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            car = client.cars[car_id]
            if car:
                return self._lua.table_from(car['pos'])
            return self._lua.table(), "Vehicle not found"
        return self._lua.table(), "Client expired"

    def IsPlayerConnected(self, player_id):
        self.log.debug("request IsPlayerConnected()")
        if player_id < 0:
            return False
        return bool(ev.call_event("_get_player", cid=player_id)[0])

    def GetPlayerName(self, player_id):
        self.log.debug("request GetPlayerName()")
        if player_id < 0:
            return None
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            return client.nick
        return

    def RemoveVehicle(self, player_id, vehicle_id):
        self.log.debug("request RemoveVehicle()")
        if player_id < 0:
            return
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            t = self.loop.create_task(client._delete_car(car_id=vehicle_id))
            self.tasks.append(t)

    def GetPlayerVehicles(self, player_id):
        self.log.debug("request GetPlayerVehicles()")
        if player_id < 0:
            return self._lua.table()
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            return self._lua.table_from(
                {i: f'{v["json"]}' for i, d in enumerate([i for i in client.cars if i is not None]) for k, v in
                 d.items() if k == "json"})

    def GetPlayers(self):
        self.log.debug("request GetPlayers()")
        clients = ev.call_event("_get_players", cid=-1)
        return self._lua.table_from({i: n for i, n in enumerate(clients)})

    def IsPlayerGuest(self, player_id) -> bool:
        self.log.debug("request IsPlayerGuest()")
        if player_id < 0:
            return True
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            return client.guest
        return False

    def DropPlayer(self, player_id, reason="Kicked"):
        self.log.debug("request DropPlayer()")
        if player_id < 0:
            return
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            t = self.loop.create_task(client.kick(reason))
            self.tasks.append(t)

    def GetStateMemoryUsage(self):
        self.log.debug("request GetStateMemoryUsage()")
        return self._lua.get_memory_used()

    def GetLuaMemoryUsage(self):
        self.log.debug("request GetStateMemoryUsage()")
        lua_plugins = ev.call_event("_lua_plugins_get")[0]
        return sum(pl['lua'].get_memory_used() for pls in lua_plugins.values() for pl in pls.values())

    def GetPlayerIdentifiers(self, player_id):
        self.log.debug("request GetStateMemoryUsage()")
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            return self._lua.table_from(client.identifiers)
        return self._lua.table()

    def Set(self, *args):
        self.log.debug("request Set")
        self.log.warning("KuiToi cannot support this: MP.Set()")

    def Settings(self, *args):
        self.log.debug("request Set")
        self.log.warning("KuiToi cannot support this: MP.Settings()")


# noinspection PyPep8Naming
class Util:
    def __init__(self, name, lua):
        self.log = get_logger(f"LuaPlugin | Util | {name}")
        self.name = name
        self._lua = lua

    def JsonEncode(self, table):
        self.log.debug("requesting JsonEncode()")

    def JsonDecode(self, string):
        self.log.debug("requesting JsonDecode()")

    def JsonPrettify(self, string):
        self.log.debug("requesting JsonPrettify()")

    def JsonMinify(self, string):
        self.log.debug("requesting JsonMinify()")

    def JsonFlatten(self, string):
        self.log.debug("requesting JsonFlatten()")

    def JsonUnflatten(self, string):
        self.log.debug("requesting JsonUnflatten()")

    def JsonDiff(self, a, b):
        self.log.debug("requesting JsonDiff()")

    def JsonDiffApply(self, base, diff):
        self.log.debug("requesting JsonDiffApply()")

    def Random(self) -> int:
        self.log.debug("requesting Random()")
        return random.randint(0, 1)

    def RandomIntRange(self, min_v, max_v):
        self.log.debug("requesting RandomIntRange()")

    def RandomRange(self, min_v, max_v):
        self.log.debug("requesting RandomRange()")


# noinspection PyPep8Naming
class FP:

    def __init__(self, name: str, lua: LuaRuntime):
        self.log = get_logger(f"LuaPlugin | FP | {name}")
        self.name = name
        self._lua = lua

    def CreateDirectory(self, path):
        self.log.debug("requesting CreateDirectory()")
        try:
            os.makedirs(path)
            return True, None
        except FileNotFoundError | NotADirectoryError as e:
            return False, f"{e}"
        except PermissionError as e:
            return False, f"{e}"
        except OSError as e:
            return False, f"{e}"
        except TypeError as e:
            return False, f"{e}"
        except ValueError as e:
            return False, f"{e}"

    def Remove(self, path):
        self.log.debug("requesting Remove()")
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            return True, None
        except (FileNotFoundError, NotADirectoryError) as e:
            return False, f"{e}"
        except PermissionError as e:
            return False, f"{e}"
        except OSError as e:
            return False, f"{e}"
        except TypeError as e:
            return False, f"{e}"

    def Rename(self, path_from, path_to):
        self.log.debug("requesting Rename()")
        try:
            os.rename(path_from, path_to)
            return True, None
        except (FileNotFoundError, NotADirectoryError) as e:
            return False, f"{e}"
        except PermissionError as e:
            return False, f"{e}"
        except OSError as e:
            return False, f"{e}"
        except TypeError as e:
            return False, f"{e}"

    def Copy(self, path_from, path_to):
        self.log.debug("requesting Copy()")
        try:
            if os.path.isfile(path_from):
                shutil.copy2(path_from, path_to)
            elif os.path.isdir(path_from):
                shutil.copytree(path_from, path_to)
            else:
                raise ValueError("Invalid path: {}".format(path_from))
            return True, None
        except (FileNotFoundError, NotADirectoryError, shutil.Error) as e:
            return False, f"{e}"
        except PermissionError as e:
            return False, f"{e}"
        except OSError as e:
            return False, f"{e}"
        except TypeError as e:
            return False, f"{e}"

    def GetFilename(self, path):
        self.log.debug("requesting GetFilename()")
        return os.path.basename(path)

    def GetExtension(self, path):
        self.log.debug("requesting GetExtension()")
        return os.path.splitext(path)[1]

    def GetParentFolder(self, path):
        self.log.debug("requesting GetParentFolder()")
        return os.path.dirname(path)

    def Exists(self, path):
        self.log.debug("requesting Exists()")
        return os.path.exists(path)

    def IsDirectory(self, path):
        self.log.debug("requesting IsDirectory()")
        return os.path.isdir(path)

    def IsFile(self, path):
        self.log.debug("requesting IsFile()")
        return os.path.isfile(path)

    def ListDirectories(self, path):
        self.log.debug("requesting ListDirectories()")
        directories = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                directories.append(item)
        return self._lua.table_from({i: v for i, v in enumerate(directories)})

    def ListFiles(self, path):
        self.log.debug("requesting ListFiles()")
        files = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                files.append(item)
        return self._lua.table_from({i: v for i, v in enumerate(files)})

    def ConcatPaths(self, *args):
        self.log.debug("requesting ConcatPaths()")
        return os.path.join(*args)


class LuaPluginsLoader:

    def __init__(self, plugins_dir):
        self.loop = asyncio.get_event_loop()
        self.plugins_dir = plugins_dir
        self.lua_plugins = {}
        self.lua_plugins_tasks = []
        self.lua_dirs = []
        self.log = get_logger("LuaPluginsLoader")
        self.loaded_str = "Lua plugins: "
        ev.register_event("_lua_plugins_get", lambda x: self.lua_plugins)
        ev.register_event("_lua_plugins_start", self.start)
        ev.register_event("_lua_plugins_unload", self.unload)
        console.add_command("lua_plugins", lambda x: self.loaded_str[:-2])
        console.add_command("lua_pl", lambda x: self.loaded_str[:-2])

    async def load(self):
        self.log.debug("Loading Lua plugins...")
        py_folders = ev.call_event("_plugins_get")[0]
        for obj in os.listdir(self.plugins_dir):
            path = os.path.join(self.plugins_dir, obj)
            if os.path.isdir(path) and obj not in py_folders and obj not in "__pycache__":
                if os.path.isfile(os.path.join(path, "main.lua")):
                    self.lua_dirs.append([path, obj])

        self.log.debug(f"py_folders {py_folders}, lua_dirs {self.lua_dirs}")

        for path, obj in self.lua_dirs:
            # noinspection PyArgumentList
            lua = LuaRuntime(encoding=config.enc, source_encoding=config.enc, unpack_returned_tuples=True)
            lua.globals().printRaw = lua.globals().print
            lua.globals().exit = lambda x: self.log.info(f"{obj}: You can't disable server..")
            mp = MP(obj, lua)
            lua.globals().MP = mp
            lua.globals().print = mp._print
            lua.globals().Util = Util(obj, lua)
            lua.globals().FP = FP(obj, lua)
            code = f'package.path = package.path.."' \
                   f';{self.plugins_dir}/{obj}/?.lua' \
                   f';{self.plugins_dir}/{obj}/lua/?.lua"\n'
            with open("modules/PluginsLoader/add_in.lua", "r") as f:
                code += f.read()
            with open(os.path.join(path, "main.lua"), 'r', encoding=config.enc) as f:
                code += f.read()
            try:
                lua.execute(code)
                self.loaded_str += f"{obj}:ok, "
                self.lua_plugins.update({obj: {"mp": mp, "lua": lua}})
            except Exception as e:
                self.log.error(f"Cannot load lua plugin from `{obj}/main.lua`")
                self.log.exception(e)
                self.loaded_str += f"{obj}:no, "

    async def start(self, _):
        ...

    async def unload(self, _):
        ...
