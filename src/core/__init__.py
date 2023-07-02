# Developed by KuiToi Dev
# File core.__init__.py
# Written by: SantaSpeen
# Version 1.1
# Licence: FPA
# (c) kuitoi.su 2023

__title__ = 'KuiToi-Server'
__description__ = 'BeamingDrive Multiplayer server compatible with BeamMP clients.'
__url__ = 'https://github.com/kuitoi/kuitoi-Server'
__version__ = '0.1.1'
__build__ = 176
__author__ = 'SantaSpeen'
__author_email__ = 'admin@kuitoi.su'
__license__ = "FPA"
__copyright__ = 'Copyright 2023 © SantaSpeen (Maxim Khomutov)'

import asyncio
import builtins
import os
import webbrowser

from prompt_toolkit.shortcuts import input_dialog, yes_no_dialog

from modules import ConfigProvider
from main import parser
from modules import Console
from core.core import Core
from core.utils import get_logger

loop = asyncio.get_event_loop()

console = Console()
log = get_logger("init")

log.info("Hello from KuiToi-Server!")
args = parser.parse_args()
if args.version:
    print(f"KuiToi-Server:\n\tVersion: {__version__}\n\tBuild: {__build__}")
    exit(0)

config_path = "kuitoi.yml"
if args.config:
    config_path = args.config
log.info(f"Use {config_path} for config.")
config_provider = ConfigProvider(config_path)
config = config_provider.open_config()
if config.Server['debug'] is True:
    core.utils.set_debug_status()
    log.info("Getting new logging with DEBUG level!")
    log = get_logger("main")
    log.debug("Debug mode enabled!")
    log.debug(f"Server config: {config}")

if not config.Auth['key']:
    log.warn("Key needed for starting the server!")
    url = "https://beammp.com/k/keys"
    if yes_no_dialog(
            title='BEAMP Server Key',
            text='Key needed for starting the server!\n'
                 'Do you need to open the web link to obtain the key?').run():
        webbrowser.open(url, new=2)

    config.Auth['key'] = input_dialog(
        title='BEAMP Server Key',
        text='Please type your key:').run()
    config_provider.save_config()
if not config.Auth['key']:
    log.error("Key is empty!")
    log.error("Server stopped!")
    exit(1)

builtins.config = config
console.builtins_hook()
console.logger_hook()
console.add_command("stop", console.stop, "stop - Just shutting down the server.\nUsage: stop", "Server shutdown.")
console.add_command("exit", console.stop, "stop - Just shutting down the server.\nUsage: stop", "Server shutdown.")

if not os.path.exists("mods"):
    os.mkdir("mods")
if not os.path.exists("plugins"):
    os.mkdir("plugins")

log.info("Initializing ready.")
