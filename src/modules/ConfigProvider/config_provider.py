# -*- coding: utf-8 -*-
# Developed by KuiToi Dev
# File modules.config_provider.config_provider.py
# Written by: SantaSpeen
# Version 1.1
# Licence: FPA
# (c) kuitoi.su 2023
import os
import secrets

import yaml


class Config:
    def __init__(self, auth=None, game=None, server=None, options=None, web=None):
        self.Auth = auth or {"key": None, "private": True}
        self.Game = game or {"map": "gridmap_v2", "players": 8, "max_cars": 1}
        self.Server = server or {"name": "KuiToi-Server", "description": "Welcome to KuiToi Server!",
                                 "server_ip": "0.0.0.0", "server_port": 30814}
        self.Options = options or {"language": "en", "encoding": "utf-8", "speed_limit": 0, "use_queue": False,
                                   "debug": False, "use_lua": False, "log_chat": True}
        self.WebAPI = web or {"enabled": False, "server_ip": "127.0.0.1", "server_port": 8433,
                              "secret_key": secrets.token_hex(16)}

    def __repr__(self):
        return "%s(Auth=%r, Game=%r, Server=%r)" % (self.__class__.__name__, self.Auth, self.Game, self.Server)


class ConfigProvider:

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = Config()

    def open_config(self):
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f)
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.load(f.read(), yaml.Loader)
        except yaml.YAMLError:
            print("You have errors in the YAML syntax.")
            print("Stopping server.")
            exit(1)

        return self.config

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f)
