# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File modules.i18n.i18n.py
# Written by: SantaSpeen
# Version 1.0
# Licence: FPA
# (c) kuitoi.su 2023
import builtins
import json
from json import JSONDecodeError

from core.utils import get_logger


class i18n:

    def __init__(self, data):
        # Basic phases
        self.hello: str = data["hello"]
        self.config_path: str = data["config_path"]
        self.init_ok: str = data["init_ok"]
        self.start: str = data["start"]
        self.stop: str = data["stop"]

        # Server auth
        self.auth_need_key: str = data["auth_need_key"]
        self.auth_empty_key: str = data["auth_empty_key"]
        self.auth_cannot_open_browser: str = data["auth_cannot_open_browser"]
        self.auth_use_link: str = data["auth_use_link"]

        # GUI phases
        self.GUI_yes: str = data["GUI_yes"]
        self.GUI_no: str = data["GUI_no"]
        self.GUI_ok: str = data["GUI_ok"]
        self.GUI_cancel: str = data["GUI_cancel"]
        self.GUI_need_key_message: str = data["GUI_need_key_message"]
        self.GUI_enter_key_message: str = data["GUI_enter_key_message"]
        self.GUI_cannot_open_browser: str = data["GUI_cannot_open_browser"]

        # Web phases
        self.web_start: str = data["web_start"]

        # Command: man
        self.man_message_man: str = data["man_message_man"]
        self.help_message_man: str = data["help_message_man"]
        self.man_for: str = data["man_for"]
        self.man_message_not_found: str = data["man_message_not_found"]
        self.man_command_not_found: str = data["man_command_not_found"]

        # Command: help
        self.man_message_help: str = data["man_message_help"]
        self.help_message_help: str = data["help_message_help"]
        self.help_command: str = data["help_command"]
        self.help_message: str = data["help_message"]
        self.help_message_not_found: str = data["help_message_not_found"]

        # Command: help
        self.man_message_stop: str = data["man_message_stop"]
        self.help_message_stop: str = data["help_message_stop"]

        # Command: exit
        self.man_message_exit: str = data["man_message_exit"]
        self.help_message_exit: str = data["help_message_exit"]

        self.data = data


class MultiLanguage:

    def __init__(self, language: str = None, files_dir="modules/i18n/files/", encoding="utf-8"):
        if language is None:
            language = "en"
        self.__data = {}
        self.__i18n = None
        self.__encoding = encoding
        self.language = language
        self.files_dir = files_dir
        self.log = get_logger("i18n")
        self.set_language(language)

    def set_language(self, language):
        if language is None:
            language = "en"
        self.log.debug(f"set_language({language})")
        self.language = language
        if language != "en":
            self.open_file()
        else:
            # noinspection PyDictDuplicateKeys
            self.__data = {
                "": "Basic phases",
                "hello": "Hello from KuiToi-Server!",
                "config_path": "Use {} for config.",
                "init_ok": "Initializing ready.",
                "start": "Server started!",
                "stop": "Goodbye!",

                "": "Server auth",
                "auth_need_key": "BEAM key needed for starting the server!",
                "auth_empty_key": "Key is empty!",
                "auth_cannot_open_browser": "Cannot open browser: {}",
                "auth_use_link": "Use this link: {}",

                "": "GUI phases",
                "GUI_yes": "Yes",
                "GUI_no": "No",
                "GUI_ok": "Ok",
                "GUI_cancel": "Cancel",
                "GUI_need_key_message": "BEAM key needed for starting the server!\nDo you need to open the web link to obtain the key?",
                "GUI_enter_key_message": "Please type your key:",
                "GUI_cannot_open_browser": "Cannot open browser.\nUse this link: {}",

                "": "Web phases",
                "web_start": "WebAPI running on {} (Press CTRL+C to quit)",

                "": "Command: man",
                "man_message_man": "man - display the manual page for COMMAND.\nUsage: man COMMAND",
                "help_message_man": "Display the manual page for COMMAND.",
                "man_for": "Manual for command",
                "man_message_not_found": "man: Manual message not found.",
                "man_command_not_found": "man: command \"{}\" not found!",

                "": "Command: help",
                "man_message_help": "help - display names and brief descriptions of available commands.\nUsage: help [--raw]\nThe `help` command displays a list of all available commands along with a brief description of each command.",
                "help_message_help": "Display names and brief descriptions of available commands",
                "help_command": "Command",
                "help_message": "Help message",
                "help_message_not_found": "No help message found",

                "": "Command: stop",
                "man_message_stop": "stop - Just shutting down the server.\nUsage: stop",
                "help_message_stop": "Server shutdown.",

                "": "Command: exit",
                "man_message_exit": "exit - Just shutting down the server.\nUsage: stop",
                "help_message_exit": "Server shutdown."
            }
        self.__i18n = i18n(self.__data)

    def open_file(self):
        self.log.debug("open_file")
        file = self.files_dir + self.language + ".json"
        try:
            with open(file, encoding=self.__encoding) as f:
                self.__data.update(json.load(f))
            return
        except JSONDecodeError:
            self.log.error(
                f"Localisation \"{self.language}.json\" have JsonDecodeError. Using default localisation: en.")
        except FileNotFoundError:
            self.log.warning(f"Localisation \"{self.language}.json\" not found; Using default localisation: en.")
        self.set_language("en")

    def builtins_hook(self) -> None:
        self.log.debug("used builtins_hook")
        builtins.i18n = self.__i18n
        builtins.i18n_data = self.__data
