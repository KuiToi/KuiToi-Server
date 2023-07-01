# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File modules.config_provider.config_provider.py
# Written by: SantaSpeen
# Version 1.0
# Licence: FPA
# (c) kuitoi.su 2023
import os

import yaml


class Config:
    def __init__(self, auth=None, game=None, server=None):
        self.Auth = auth or {"key": None, "private": True}
        self.Game = game or {"map": "gridmap_v2", "players": 8, "max_cars": 1}
        self.Server = server or {"name": "KuiToi-Server",
                                 "description": "This server uses KuiToi!",
                                 "port": 30814, "server_ip": "0.0.0.0", "debug": False}

    def __repr__(self):
        return "%s(Auth=%r, Game=%r, Server=%r)" % (self.__class__.__name__, self.Auth, self.Game, self.Server)


class ConfigProvider:

    def __init__(self, config_patch):
        self.config_patch = config_patch
        self.config = Config()

    def open_config(self):
        if not os.path.exists(self.config_patch):
            with open(self.config_patch, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f)
        try:
            with open(self.config_patch, "r", encoding="utf-8") as f:
                self.config = yaml.load(f.read(), yaml.Loader)
        except yaml.YAMLError:
            print("You have errors in the YAML syntax.")
            print("Stopping server.")
            exit(1)

        return self.config

    def save_config(self):
        with open(self.config_patch, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f)
