import asyncio
import json
import os
import platform
import random
import shutil
from threading import Thread

from lupa.lua53 import LuaRuntime

from core import get_logger


# noinspection PyPep8Naming
class MP:

    # In ./in_lua.lua
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
        args = list(args)
        for i, arg in enumerate(args):
            if "LuaTable" in str(type(arg)):
                args[i] = self._lua.globals().Util.JsonEncode(arg)
        s = " ".join(map(str, args))
        self.log.info(s)

    def CreateTimer(self):
        self.log.debug("request CreateTimer()")
        # TODO: CreateTimer

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
        if not event_func:
            self.log.error(f"Can't register '{event_name}': not found function: '{function_name}'")
            return
        ev.register_event(event_name, event_func, lua=function_name)
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
        self.log.debug("request TriggerClientEventJson()")
        data = self._lua.globals().Util.JsonEncode(data)
        self.TriggerClientEvent(player_id, event_name, data)

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

    def GetPlayerIDByName(self, player_name):
        self.log.debug("request GetPlayerIDByName()")
        if not isinstance(player_name, str):
            return None
        client = ev.call_event("_get_player", nick=player_name)[0]
        if client:
            return client.cid
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

    def _recursive_list_encode(self, table):
        new_list = list(table.values())
        for i, v in enumerate(list(table.values())):
            if not isinstance(v, (int, float, bool, str, dict, list)) and "LuaTable" not in str(type(v)):
                new_list[i] = None
                continue
            if "LuaTable" in str(type(v)):
                d = dict(v)
                if all(isinstance(ii, int) for ii in d.keys()):
                    new_list[i] = self._recursive_list_encode(d)
                    continue
                else:
                    new_list[i] = self._recursive_dict_encode(d)
        return [i for i in new_list if i is not None]

    def _recursive_dict_encode(self, table):
        new_dict = dict(table)
        for k, v in table.items():
            if not isinstance(v, (int, float, bool, str, dict, list)) and "LuaTable" not in str(type(v)):
                new_dict[k] = None
                continue
            if "LuaTable" in str(type(v)):
                d = dict(v)
                if all(isinstance(i, int) for i in d.keys()):
                    new_dict[k] = self._recursive_list_encode(d)
                    continue
                else:
                    new_dict[k] = self._recursive_dict_encode(d)
        return {k: v for k, v in new_dict.items() if v is not None}

    def JsonEncode(self, table):
        self.log.debug("requesting JsonEncode()")
        if all(isinstance(k, int) for k in table.keys()):
            data = self._recursive_list_encode(table)
        else:
            data = self._recursive_dict_encode(table)
        return json.dumps(data)

    def JsonDecode(self, string):
        self.log.debug("requesting JsonDecode()")
        return self._lua.table_from(json.loads(string))

    def JsonPrettify(self, string):
        self.log.debug("requesting JsonPrettify()")
        data = json.loads(string)
        return json.dumps(data, indent=4, sort_keys=True)

    def JsonMinify(self, string):
        self.log.debug("requesting JsonMinify()")
        data = json.loads(string)
        return json.dumps(data, separators=(',', ':'))

    def JsonFlatten(self, json_str):
        self.log.debug("request JsonFlatten()")
        json_obj = json.loads(json_str)
        flat_obj = {}

        def flatten(obj, path=''):
            if isinstance(obj, dict):
                for key in obj:
                    flatten(obj[key], path + '/' + key)
            elif isinstance(obj, list):
                for i in range(len(obj)):
                    flatten(obj[i], path + '/' + str(i))
            else:
                flat_obj[path] = obj

        flatten(json_obj)
        flat_json = json.dumps(flat_obj)
        return flat_json

    def JsonUnflatten(self, flat_json):
        self.log.debug("request JsonUnflatten")
        flat_obj = json.loads(flat_json)

        def unflatten(obj):
            result = {}
            for key in obj:
                parts = key.split('/')
                d = result
                for part in parts[:-1]:
                    if part not in d:
                        # create a new node in the dictionary
                        # if the path doesn't exist
                        d[part] = {}
                    d = d[part]
                # assign the value to the last part of the path
                d[parts[-1]] = obj[key]
            return result

        json_obj = unflatten(flat_obj)
        return json.dumps(json_obj)

    def JsonDiff(self, a: str, b: str) -> str:
        self.log.debug("requesting JsonDiff()")
        a_obj = json.loads(a)
        b_obj = json.loads(b)
        diff = []
        for k, v in b_obj.items():
            if k not in a_obj:
                diff.append({"op": "add", "path": "/" + k, "value": v})
            elif a_obj[k] != v:
                diff.append({"op": "replace", "path": "/" + k, "value": v})
        for k in a_obj.keys() - b_obj.keys():
            diff.append({"op": "remove", "path": "/" + k})
        return json.dumps(diff)

    @staticmethod
    def _apply_patch(base_obj, patch_obj):
        for patch in patch_obj:
            op = patch['op']
            path = patch['path']
            value = patch.get('value', None)
            tokens = path.strip('/').split('/')
            obj = base_obj
            for i, token in enumerate(tokens):
                if isinstance(obj, list):
                    token = int(token)
                if i == len(tokens) - 1:
                    if op == 'add':
                        if isinstance(obj, list):
                            obj.insert(int(token), value)
                        else:
                            obj[token] = value
                    elif op == 'replace':
                        obj[token] = value
                    elif op == 'remove':
                        if isinstance(obj, list):
                            obj.pop(int(token))
                        else:
                            del obj[token]
                else:
                    obj = obj[token]
        return base_obj

    def JsonDiffApply(self, base: str, diff: str) -> str:
        self.log.debug("requesting JsonDiffApply()")
        base_obj = json.loads(base)
        diff_obj = json.loads(diff)
        result = self._apply_patch(base_obj, diff_obj)
        return json.dumps(result)

    def Random(self) -> float:
        self.log.debug("requesting Random()")
        return random.random()

    def RandomIntRange(self, min_v, max_v) -> int:
        self.log.debug("requesting RandomIntRange()")
        return random.randint(min_v, max_v)

    def RandomRange(self, min_v, max_v) -> float:
        self.log.debug("requesting RandomRange()")
        return random.uniform(min_v, max_v)


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
        ev.register_event("_lua_plugins_unload", self.unload)
        console.add_command("lua_plugins", lambda x: self.loaded_str[:-2])
        console.add_command("lua_pl", lambda x: self.loaded_str[:-2])

    def _start(self, obj, lua, file):
        try:
            lua.globals().loadfile(f"plugins/{obj}/{file}")()
            self.lua_plugins[obj]['ok'] = True
            self.loaded_str += f"{obj}:ok, "
            lua.globals().onInit()
            lua.globals().MP.TriggerLocalEvent("onInit")
        except Exception as e:
            self.loaded_str += f"{obj}:no, "
            self.log.error(f"Cannot load lua plugin from `{obj}/main.lua`\n{e}")
            # self.log.exception(e)

    def load(self):
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
            lua_globals = lua.globals()
            lua_globals.printRaw = lua.globals().print
            lua_globals.exit = lambda x: self.log.info(f"{obj}: You can't disable server..")
            mp = MP(obj, lua)
            lua_globals.MP = mp
            lua_globals.print = mp._print
            lua_globals.Util = Util(obj, lua)
            lua_globals.FP = FP(obj, lua)
            pa = os.path.abspath(self.plugins_dir)
            p0 = os.path.join(pa, obj, "?.lua")
            p1 = os.path.join(pa, obj, "lua", "?.lua")
            lua_globals.package.path += f';{p0};{p1}'
            # with open("modules/PluginsLoader/add_in.lua", "r") as f:
            #     code += f.read()
            self.lua_plugins.update({obj: {"mp": mp, "lua": lua, "thread": None, "ok": False}})
            th = Thread(target=self._start, args=(obj, lua, "main.lua"), name=f"lua_plugin_{obj}-Thread")
            th.start()
            self.lua_plugins[obj]['thread'] = th

    def unload(self, _):
        ...
