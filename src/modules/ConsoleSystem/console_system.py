# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File core.config_provider.py
# Written by: SantaSpeen
# Version 1.1
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio
import builtins
import logging
from typing import AnyStr

from prompt_toolkit import PromptSession, print_formatted_text, HTML
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory


class Console:

    def __init__(self,
                 prompt_in="> ",
                 prompt_out="",
                 not_found="Command \"%s\" not found in alias.",
                 debug=False) -> None:
        self.__is_run = False
        self.__prompt_in = prompt_in
        self.__prompt_out = prompt_out
        self.__not_found = not_found
        self.__is_debug = debug
        self.__print = print
        self.__func = dict()
        self.__alias = dict()
        self.__man = dict()
        self.__desc = dict()
        self.add_command("man", self.__create_man_message, "man - display the manual page.\n"
                                                           "Usage: man COMMAND", "Display the manual page",
                         custom_completer={"man": {}})
        self.add_command("help", self.__create_help_message,
                         "help - display names and brief descriptions of available commands.\n"
                         "Usage: help [--raw]\n"
                         "The `help` command displays a list of all available commands along with a brief description "
                         "of each command.", "Display names and brief descriptions of available commands.",
                         custom_completer={"help": {"--raw": None}})
        self.completer = NestedCompleter.from_nested_dict(self.__alias)

    def __debug(self, *x):
        if self.__is_debug:
            x = list(x)
            x.insert(0, "\r CONSOLE DEBUG:")
            self.__print(*x)

    def __getitem__(self, item):
        print(item)

    @staticmethod
    def __get_max_len(arg) -> int:
        i = 0
        arg = list(arg)
        for a in arg:
            ln = len(str(a))
            if ln > i:
                i = ln
        return i

    def __create_man_message(self, argv: list) -> AnyStr:
        x = argv[0]
        if x in ['']:
            return "man COMMAND"
        man_message = self.__man.get(x)
        if man_message is None:
            return "man: Manual message not found."
        if man_message:
            return man_message
        return f'man: command "{x}" not found'

    def __create_help_message(self, argv: list) -> AnyStr:
        self.__debug("creating help message")
        raw = False
        max_len_v = 0
        if "--raw" in argv:
            max_len_v = self.__get_max_len(self.__func.values())
            print()
            raw = True

        message = str()
        max_len = self.__get_max_len(self.__func.keys())
        if max_len < 7:
            max_len = 7

        if raw:
            message += f"%-{max_len}s; %-{max_len_v}s; %s\n" % ("Key", "Function", "Description")
        else:
            message += f"   %-{max_len}s : %s\n" % ("Command", "Help message")

        for k, v in self.__func.items():
            doc = self.__desc.get(k)

            if raw:
                message += f"%-{max_len}s; %-{max_len_v}s; %s\n" % (k, v, doc)

            else:
                if doc is None:
                    doc = "No help message found"
                message += f"   %-{max_len}s : %s\n" % (k, doc)

        return message

    def __update_completer(self):
        self.completer = NestedCompleter.from_nested_dict(self.__alias)

    def add_command(self, key: str, func, man: str = None, desc: str = None, custom_completer: dict = None) -> dict:
        key = key.format(" ", "-")

        if not isinstance(key, str):
            raise TypeError("key must be string")
        self.__debug(f"added user command: key={key}; func={func};")
        self.__alias.update(custom_completer or {key: None})
        self.__alias["man"].update({key: None})
        self.__func.update({key: {"f": func}})
        self.__man.update({key: f'html<seagreen>Manual for command <b>{key}</b>\n{man}</seagreen>' if man else None})
        self.__desc.update({key: desc})
        self.__update_completer()
        return self.__alias.copy()

    def write(self, s: AnyStr):
        if s.startswith("html"):
            print_formatted_text(HTML(s[4:]))
        else:
            print_formatted_text(s)

    def log(self, s: AnyStr) -> None:
        self.write(s)

    def __lshift__(self, s: AnyStr) -> None:
        self.write(s)

    @property
    def alias(self) -> dict:
        return self.__alias.copy()

    def __builtins_print(self,
                         *values: object,
                         sep: str or None = " ",
                         end: str or None = None,
                         file: str or None = None,
                         flush: bool = False,
                         loading: bool = False) -> None:
        self.__debug(f"Used __builtins_print; is_run: {self.__is_run}")
        val = list(values)
        if len(val) > 0:
            val.insert(0, "\r" + self.__prompt_out)
            if not loading:
                if self.__is_run:
                    val.append("\r\n" + self.__prompt_in + " ")
                    end = "" if end is None else end
                else:
                    if end is None:
                        end = "\n"
        self.__print(*tuple(val), sep=sep, end=end, file=file, flush=flush)

    def logger_hook(self) -> None:
        self.__debug("used logger_hook")

        def emit(cls, record):
            try:
                msg = cls.format(record)
                if cls.stream.name == "<stderr>":
                    self.write(f"{msg}")
                else:
                    cls.stream.write(msg + cls.terminator)
                cls.flush()
            except RecursionError:
                raise
            except Exception as e:
                cls.handleError(record)

        logging.StreamHandler.emit = emit

    def builtins_hook(self) -> None:
        self.__debug("used builtins_hook")

        builtins.Console = Console
        builtins.console = self

        builtins.print = self.__builtins_print

    async def read_input(self):
        session = PromptSession(history=FileHistory('./.cmdhistory'))
        while True:
            try:
                cmd_in = await session.prompt_async(self.__prompt_in,
                                                    completer=self.completer, auto_suggest=AutoSuggestFromHistory())
                cmd_s = cmd_in.split(" ")
                cmd = cmd_s[0]
                if cmd == "":
                    pass
                else:
                    command_object = self.__func.get(cmd)
                    if command_object:
                        self.log(str(command_object['f'](cmd_s[1:])))
                    else:
                        self.log(self.__not_found % cmd)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as e:
                print(f"Error in console.py: {e}")

    async def start(self):
        self.__is_run = True
        await self.read_input()

    def stop(self, *args, **kwargs):
        self.__is_run = False
        raise KeyboardInterrupt


if __name__ == '__main__':
    c = Console()
    c.logger_hook()
    c.builtins_hook()
    log = logging.getLogger(name="name")
    log.info("Starting console")
    print("Starting console")
    asyncio.run(c.start())
