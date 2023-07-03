# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File modules.i18n.i18n.py
# Written by: SantaSpeen
# Version 1.0
# Licence: FPA
# (c) kuitoi.su 2023
import builtins
import json

from core import get_logger


class i18n:

    def __init__(self, data):
        self.hello: str = data["hello"]
        self.config_file: str = data["config_file"]
        self.debug: str = data["debug"]
        self.config_info: str = data["config_info"]
        self.init: str = data["init"]
        self.ready: str = data["ready"]


class MultiLanguage:

    def __init__(self, language: str = None, files_dir="modules/i18n/files/"):
        if language is None:
            language = "en"
        self.__data = {}
        self.__i18n = None
        self.language = language
        self.files_dir = files_dir
        self.log = get_logger("i18n")
        self.set_language(language)

    def set_language(self, language):
        if language is None:
            return
        self.log.debug(f"set_language({language})")
        self.language = language
        if language != "en":
            self.open_file()
        else:
            self.__data = {
                "hello": "Hello from KuiToi-Server!",
                "config_file": "Use kuitoi.yml for config.",
                "debug": "Getting new logging with DEBUG level!",
                "config_info": "Server config: %s",
                "init": "Initializing ready.",
                "ready": "Server started!"
            }
        self.__i18n = i18n(self.__data)

    def open_file(self):
        self.log.debug("open_file")
        file = self.files_dir + self.language + ".json"
        try:
            with open(file) as f:
                self.__data.update(json.load(f))
        except FileNotFoundError:
            self.log.warning(f"Localisation {self.language} not found; Setting language to: en.")
            self.set_language("en")

    def builtins_hook(self) -> None:
        self.log.debug("used builtins_hook")
        builtins.i18n = self.__i18n
        builtins.i18n_data = self.__data
