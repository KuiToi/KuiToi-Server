import asyncio
import os

# noinspection PyUnresolvedReferences
import lupa.lua53
from lupa.lua53 import LuaRuntime

from core import get_logger


class MP:

    def __init__(self, name):
        self.name = name
        self.log = get_logger(f"LuaPlugin | {name}")

    def log_info(self, *args):
        s = ""
        for i in args:
            s += i
        self.log.info(s)


class LuaPluginsLoader:

    def __init__(self, plugins_dir):
        self.loop = asyncio.get_event_loop()
        self.plugins_dir = plugins_dir
        self.lua_plugins = {}
        self.lua_plugins_tasks = []
        self.lua_dirs = []
        self.log = get_logger("LuaPluginsLoader")
        self.loaded_str = "Lua plugins: "
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
            lua = LuaRuntime(encoding=config.enc, source_encoding=config.enc)
            mp = MP(obj)
            lua.globals().MP = mp
            lua.globals().print = mp.log_info
            code = f'package.path = package.path.."' \
                   f';{self.plugins_dir}/{obj}/?.lua' \
                   f';{self.plugins_dir}/{obj}/lua/?.lua' \
                   f';modules/PluginsLoader/lua_libs/?.lua"'
            with open(os.path.join(path, "main.lua"), 'r', encoding=config.enc) as f:
                code += f.read()
            lua.execute(code)

    async def start(self, _):
        ...

    async def unload(self, _):
        ...
