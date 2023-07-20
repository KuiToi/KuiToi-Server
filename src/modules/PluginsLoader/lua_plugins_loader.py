import asyncio
import os

from core import get_logger


class MP:

    def __init__(self):
        pass


class LuaPluginsLoader:

    def __init__(self, plugins_dir):
        self.loop = asyncio.get_event_loop()
        self.lua_plugins = {}
        self.lua_plugins_tasks = []
        self.plugins_dir = plugins_dir
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
        folders = []
        for obj in os.listdir(self.plugins_dir):
            path = os.path.join(self.plugins_dir, obj)
            if os.path.isdir(path) and obj not in py_folders and obj not in "__pycache__":
                if os.path.isfile(os.path.join(path, "main.lua")):
                    folders.append(path)

        self.log.debug(f"py_folders {py_folders}, folders {folders}")

        # for dirpath, dirnames, filenames in os.walk(f"/{self.plugins_dir}/{plugin_dir}"):
        #     if "main.lua" in filenames:
        #         return os.path.join(dirpath, "main.lua")

    async def start(self, _): ...
    async def unload(self, _): ...
