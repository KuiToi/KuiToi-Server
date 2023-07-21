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
            if event_name not in self.__lua_events:
                self.__lua_events.update({str(event_name): [event_func]})
            else:
                self.__lua_events[event_name].append(event_func)
            self.log.debug("Register ok")
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
            self.log.debug("Register ok")
        else:
            if event_name not in self.__events:
                self.__events.update({str(event_name): [event_func]})
            else:
                self.__events[event_name].append(event_func)
            self.log.debug("Register ok")

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

    def call_lua_event(self, event_name, *args):
        self.log.debug(f"Calling lua event: '{event_name}'")
        funcs_data = []
        if event_name in self.__lua_events.keys():
            for func in self.__lua_events[event_name]:
                try:
                    funcs_data.append(func(*args))
                except Exception as e:
                    # TODO: i18n
                    self.log.error(f'Error while calling "{event_name}"; In function: "{func.__name__}"')
                    self.log.exception(e)
        else:
            # TODO: i18n
            self.log.warning(f"Event {event_name} does not exist, maybe ev.call_lua_event() or MP.Trigger<>Event()?. "
                             f"Just skipping it...")

        return funcs_data



