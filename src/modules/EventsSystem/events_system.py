# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File modules.EventsSystem.events_system.py
# Written by: SantaSpeen
# Version 1.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import builtins
import inspect

import lupa

from core import get_logger


# noinspection PyShadowingBuiltins
class EventsSystem:

    def __init__(self):
        # TODO: default events
        self.log = get_logger("EventsSystem")
        self.loop = asyncio.get_event_loop()
        self.as_tasks = []
        self.__events = {
            "onServerStarted": [],
            "onPlayerSentKey": [],  # Only sync
            "onPlayerAuthenticated": [],  # Only sync
            "onPlayerJoin": [],
            "onChatReceive": [],
            "onCarSpawn": [],
            "onCarDelete": [],
            "onCarEdited": [],
            "onCarReset": [],
            "onSentPing": [],  # Only sync
            "onChangePosition": [],  # Only sync
            "onServerStopped": [],
        }
        self.__async_events = {
            "onServerStarted": [],
            "onPlayerJoin": [],
            "onChatReceive": [],
            "onCarSpawn": [],
            "onCarDelete": [],
            "onCarEdited": [],
            "onCarReset": [],
            "onServerStopped": []
        }

        self.__lua_events = {
            "onInit": [],  # onServerStarted
            "onShutdown": [],  # onServerStopped
            "onPlayerAuth": [],  # onPlayerAuthenticated
            "onPlayerConnecting": [],  # TODO lua onPlayerConnecting
            "onPlayerJoining": [],  # TODO lua onPlayerJoining
            "onPlayerJoin": [],  # onPlayerJoin
            "onPlayerDisconnect": [],  # TODO lua onPlayerDisconnect
            "onChatMessage": [],  # onChatReceive
            "onVehicleSpawn": [],  # "onCarSpawn
            "onVehicleEdited": [],  # onCarEdited
            "onVehicleDeleted": [],  # onCarDelete
            "onVehicleReset": [],  # onCarReset
            "onFileChanged": [],  # TODO lua onFileChanged
        }

    def builtins_hook(self):
        self.log.debug("used builtins_hook")
        builtins.ev = self

    def register_event(self, event_name, event_func, async_event=False, lua=None):
        self.log.debug(f"register_event(event_name='{event_name}', event_func='{event_func}', "
                       f"async_event={async_event}, lua_event={lua}):")
        if lua:
            if type(event_func) != str and type(lua) != lupa.lua53.LuaRuntime:
                self.log.error(f"Cannot add event '{event_name}'. "
                               f"Use `MP.RegisterEvent(\"{event_name}\", \"function\")` instead. Skipping it...")
                return
            if event_name not in self.__lua_events:
                self.__lua_events.update({str(event_name): [{"func": event_func, "engine": lua}]})
            else:
                self.__lua_events[event_name].append(event_func)

            return

        if not callable(event_func):
            # TODO: i18n
            self.log.error(f"Cannot add event '{event_name}'. "
                           f"Use `KuiToi.add_event({event_name}', function)` instead. Skipping it...")
            return
        if async_event or inspect.iscoroutinefunction(event_func):
            if event_name not in self.__async_events:
                self.__async_events.update({str(event_name): [event_func]})
            else:
                self.__async_events[event_name].append(event_func)
        else:
            if event_name not in self.__events:
                self.__events.update({str(event_name): [event_func]})
            else:
                self.__events[event_name].append(event_func)

    async def call_async_event(self, event_name, *args, **kwargs):
        self.log.debug(f"Calling async event: '{event_name}'")
        funcs_data = []
        if event_name in self.__async_events.keys():
            for func in self.__async_events[event_name]:
                try:
                    event_data = {"event_name": event_name, "args": args, "kwargs": kwargs}
                    data = await func(event_data)
                    funcs_data.append(data)
                except Exception as e:
                    # TODO: i18n
                    self.log.error(f'Error while calling "{event_name}"; In function: "{func.__name__}"')
                    self.log.exception(e)
        else:
            # TODO: i18n
            self.log.warning(f"Event {event_name} does not exist, maybe ev.call_event()?. Just skipping it...")

        return funcs_data

    def call_event(self, event_name, *args, **kwargs):
        if event_name not in ["onChangePosition", "onSentPing"]:  # UDP events
            self.log.debug(f"Calling sync event: '{event_name}'")
        funcs_data = []

        if event_name in self.__events.keys():
            for func in self.__events[event_name]:
                try:
                    event_data = {"event_name": event_name, "args": args, "kwargs": kwargs}
                    funcs_data.append(func(event_data))
                except Exception as e:
                    # TODO: i18n
                    self.log.error(f'Error while calling "{event_name}"; In function: "{func.__name__}"')
                    self.log.exception(e)
        else:
            # TODO: i18n
            self.log.warning(f"Event {event_name} does not exist, maybe ev.call_async_event()?. Just skipping it...")

        return funcs_data

    def call_lua_event(self, *args):
        pass
