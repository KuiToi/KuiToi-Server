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
        self.plugins = {}
        self.plugins_dir = plugins_dir
        self.log = get_logger("PluginsLoader")

    def load_plugins(self):
        self.log.debug("Loading plugins...")
        files = os.listdir(self.plugins_dir)
        for file in files:
            if file.endswith(".py"):
                try:
                    self.log.debug(f"Loading plugin: {file[:-3]}")
                    plugin = types.ModuleType(file[:-3])
                    plugin.KuiToi = KuiToi
                    plugin.KuiToi._plugins_dir = self.plugins_dir
                    plugin.kt = None
                    plugin.print = print
                    file_path = os.path.join(self.plugins_dir, file)
                    plugin.__file__ = file_path
                    with open(f'{file_path}', 'r') as f:
                        code = f.read()
                        exec(code, plugin.__dict__)
                    if type(plugin.kt) != KuiToi:
                        raise AttributeError(f'Attribute "kt" isn\'t KuiToi class. Plugin file: "{file_path}"')
                    pl_name = plugin.kt.name
                    if self.plugins.get(pl_name) is not None:
                        raise NameError(f'Having plugins with identical names is not allowed; '
                                        f'Plugin name: "{pl_name}"; Plugin file "{file_path}"')
                    plugin.open = plugin.kt.open
                    plugin.load()
                    self.plugins.update({pl_name: plugin})
                    self.log.debug(f"Plugin loaded: {file}")
                except Exception as e:
                    # TODO: i18n
                    self.log.error(f"Error while loading plugin: {file}; Error: {e}")
                    self.log.exception(e)
