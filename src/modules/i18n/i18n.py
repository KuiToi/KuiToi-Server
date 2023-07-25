# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File modules.i18n.i18n.py
# Written by: SantaSpeen
# Version 1.3
# Licence: FPA
# (c) kuitoi.su 2023
import builtins
import json
from json import JSONDecodeError

from core.utils import get_logger


class i18n:
    data = {}

    def __init__(self, data):
        i18n.data = data

    def __getattribute__(self, key):
        return i18n.data[key]


class MultiLanguage:

    def __init__(self, language: str = None, files_dir="modules/i18n/files/", encoding=None):
        if encoding is None:
            encoding = config.enc
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
  "config_path": "Use {} for configuration.",
  "init_ok": "Initialization completed.",
  "start": "Server started!",
  "stop": "Server stopped!",

  "": "Server auth",
  "auth_need_key": "A BeamMP key is required to start!",
  "auth_empty_key": "BeamMP key is empty!",
  "auth_cannot_open_browser": "Failed to open browser: {}",
  "auth_use_link": "Use this link: {}",

  "": "GUI phases",
  "GUI_yes": "Yes",
  "GUI_no": "No",
  "GUI_ok": "OK",
  "GUI_cancel": "Cancel",
  "GUI_need_key_message": "A BeamMP key is required to start!\nDo you want to open the link in your browser to obtain the key?",
  "GUI_enter_key_message": "Please enter the key:",
  "GUI_cannot_open_browser": "Failed to open browser.\nUse this link: {}",

  "": "Web phases",
  "web_start": "WebAPI started on {} (CTRL+C to stop)",

  "": "Core phrases",
  "core_direct_mode": "Server started in direct connection mode.",
  "core_auth_server_error": "Incorrect response received from BeamMP authentication server.",
  "core_auth_server_refused": "BeamMP authentication server rejected your key. Reason: {}",
  "core_auth_server_refused_no_reason": "BeamMP authentication server did not provide a reason.",
  "core_auth_server_refused_direct_node": "Server is still running, but in direct connection mode.",
  "core_auth_server_no_response": "Failed to authenticate the server.",
  "core_mods_loaded": "{} mods loaded. {}Mb",

  "": "In-game phrases",
  "game_player_kicked": "Kicked for reason: \"{}\"",
  "game_welcome_message": "Welcome {}!",

  "": "Client class phrases",
  "client_mod_request": "Mod requested: {}",
  "client_mod_sent": "Mod sent: Size: {}mb, Speed: {}Mb/s ({}sec)",
  "client_mod_sent_limit": " (limit {}Mb/s)",
  "client_mod_sent_error": "Error sending mod: {}",
  "client_sync_time": "Sync time {}sec.",
  "client_event_invalid_data": "Invalid data returned from event: {}",
  "client_player_disconnected": "Disconnected from the server. Game time: {} min.",

  "": "Command: man",
  "man_message_man": "man - Shows help page for COMMAND.\nUsage: man COMMAND",
  "help_message_man": "Shows help page for COMMAND.",
  "man_for": "Help page for",
  "man_message_not_found": "man: No help page found.",
  "man_command_not_found": "man: Command \"{}\" not found!",

  "": "Command: help",
  "man_message_help": "help - Shows the names and brief descriptions of commands.\nUsage: help [--raw]\nThe `help` command displays a list of all available commands and a brief description for each command.",
  "help_message_help": "Shows the names and brief descriptions of commands.",
  "help_command": "Command",
  "help_message": "Text",
  "help_message_not_found": "No text found.",

  "": "Command: stop",
  "man_message_stop": "stop - Stops the server.\nUsage: stop",
  "help_message_stop": "Stops the server.",

  "": "Command: exit",
  "man_message_exit": "exit - Stops the server.\nUsage: exit",
  "help_message_exit": "Stops the server."
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
