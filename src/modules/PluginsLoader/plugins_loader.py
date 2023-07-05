import os
import types

from core import get_logger


class BEAMP:

    def __init__(self, name=None):
        if name is None:
            raise Exception("BEAMP: Name is required")
        self.log = get_logger(f"BEAMP({name})")
        self.name = name

    def set_name(self, name):
        self.name = name

    @staticmethod
    def register_event(event_name, event_func):
        ev.register_event(event_name, event_func)

    @staticmethod
    def call_event(event_name, *data):
        ev.call_event(event_name, *data)



class PluginsLoader:

    def __init__(self, plugins_dir):
        self.__plugins = {}
        self.__plugins_dir = plugins_dir
        self.log = get_logger("PluginsLoader")

    def load_plugins(self):
        self.log.debug("Loading plugins...")
        files = os.listdir(self.__plugins_dir)
        for file in files:
            if file.endswith(".py"):
                try:
                    self.log.debug(f"Loading plugin: {file}")
                    plugin = types.ModuleType('plugin')
                    plugin.BEAMP = BEAMP
                    file = os.path.join(self.__plugins_dir, file)
                    with open(f'{file}', 'r') as f:
                        code = f.read().replace("import BEAMP\n", "")
                        exec(code, plugin.__dict__)
                    plugin.load()
                    self.__plugins.update({file[:-3]: plugin})
                    self.log.debug(f"Plugin loaded: {file}")
                except Exception as e:
                    self.log.error(f"Error loading plugin: {file}; Error: {e}")
