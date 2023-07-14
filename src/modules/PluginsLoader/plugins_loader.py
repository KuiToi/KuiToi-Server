import os
import types
from contextlib import contextmanager

from core import get_logger


# TODO: call_client_event, get_player, get_players, GetPlayerCount
class KuiToi:
    _plugins_dir = ""

    def __init__(self, name=None):
        if name is None:
            raise AttributeError("KuiToi: Name is required")
        self.log = get_logger(f"Plugin | {name}")
        self.__name = name
        self.__dir = os.path.join(self._plugins_dir, self.__name)
        if not os.path.exists(self.__dir):
            os.mkdir(self.__dir)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        # You chell not pass
        pass

    @property
    def dir(self):
        return self.__dir

    @dir.setter
    def dir(self, value):
        # You chell not pass
        pass

    @contextmanager
    def open(self, file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
        path = os.path.join(self.__dir, file)
        if not os.path.exists(path):
            with open(path, 'x'): ...
        f = None
        try:
            f = open(path, mode, buffering, encoding, errors, newline, closefd, opener)
            yield f
        except Exception as e:
            raise e
        finally:
            if f is not None:
                f.close()

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
                    plugin.KuiToi = KuiToi
                    plugin.print = print
                    file = os.path.join(self.__plugins_dir, file)
                    with open(f'{file}', 'r') as f:
                        code = f.read().replace("import KuiToi\n", "")
                        exec(code, plugin.__dict__)
                    plugin.load()
                    self.__plugins.update({file[:-3]: plugin})
                    self.log.debug(f"Plugin loaded: {file}")
                except Exception as e:
                    self.log.error(f"Error loading plugin: {file}; Error: {e}")
