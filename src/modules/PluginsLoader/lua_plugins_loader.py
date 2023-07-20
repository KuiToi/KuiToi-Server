import asyncio
import os
import platform

import lupa
from lupa.lua53 import LuaRuntime

from core import get_logger


# noinspection PyPep8Naming
class MP:

    # In ./in_lua.lua
    # MP.CreateTimer
    # MP.Sleep

    def __init__(self, name: str, lua: LuaRuntime):
        self.loop = asyncio.get_event_loop()
        self.tasks = []
        self.name = name
        self.log = get_logger(f"LuaPlugin | {name}")
        self._lua = lua

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
        ev.register_event(event_name, function_name, lua=self._lua)

    def TriggerLocalEvent(self, event_name, *args):
        self.log.debug("request TriggerLocalEvent()")
        # TODO: TriggerLocalEvent
        return self._lua.table()

    def TriggerGlobalEvent(self, event_name, *args):
        self.log.debug("request TriggerGlobalEvent()")
        # TODO: TriggerGlobalEvent
        return self._lua.table(IsDone=lambda: True, GetResults=lambda: "somedata")

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
        # TODO: TriggerClientEvent
        self.log.debug("request TriggerClientEvent()")

    def TriggerClientEventJson(self, player_id, event_name, data):
        # TODO: TriggerClientEventJson
        self.log.debug("request TriggerClientEventJson()")

    def GetPlayerCount(self):
        self.log.debug("request GetPlayerCount()")
        return len(ev.call_event("_get_player", cid=-1)[0])

    def GetPositionRaw(self, pid, vid):
        # TODO: GetPositionRaw
        self.log.debug("request GetPositionRaw()")

    def IsPlayerConnected(self, player_id):
        self.log.debug("request IsPlayerConnected()")
        return bool(ev.call_event("_get_player", cid=player_id)[0])

    def GetPlayerName(self, player_id):
        self.log.debug("request GetPlayerName()")
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            return client.nick
        return

    def RemoveVehicle(self, player_id, vehicle_id):
        self.log.debug("request GetPlayerName()")
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            t = self.loop.create_task(client._delete_car(car_id=vehicle_id))
            self.tasks.append(t)

    def GetPlayerVehicles(self, player_id):
        self.log.debug("request GetPlayerVehicles()")
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
        client = ev.call_event("_get_player", cid=player_id)[0]
        if client:
            return client.guest
        return False

    def DropPlayer(self, player_id, reason="Kicked"):
        self.log.debug("request DropPlayer()")
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
        self.log.warning("KuiToi cannot support this")

    def Settings(self, *args):
        self.log.debug("request Set")
        self.log.warning("KuiToi cannot support this")


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
