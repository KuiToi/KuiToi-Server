# Developed by KuiToi Dev
# File core.__init__.py
# Written by: SantaSpeen
# Version 1.1
# Licence: FPA
# (c) kuitoi.su 2023

__title__ = 'KuiToi-Server'
__description__ = 'BeamingDrive Multiplayer server compatible with BeamMP clients.'
__url__ = 'https://github.com/kuitoi/kuitoi-Server'
__version__ = '0.1.2'
__build__ = 178
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
from modules import Console
from modules import MultiLanguage
from main import parser
from core.core import Core
from .utils import get_logger

args = parser.parse_args()
if args.version:
    print(f"KuiToi-Server:\n\tVersion: {__version__}\n\tBuild: {__build__}")
    exit(0)

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)
log = get_logger("init")

# i18n init
log.debug("Initializing i18n...")
ml = MultiLanguage()
ml.set_language(args.language)
ml.builtins_hook()

log.info(i18n.hello)

# Config file init
config_path = "kuitoi.yml"
if args.config:
    config_path = args.config
config_provider = ConfigProvider(config_path)
config = config_provider.open_config()
log.info(i18n.config_file % config_path)
if config.Server['debug'] is True:
    core.utils.set_debug_status()
    log.info(i18n.debug)
    log = get_logger("init")
    log.debug("Debug mode enabled!")
    log.debug(i18n.config_info % config)

# Key handler..
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

# Console Init
log.debug("Initializing console...")
console = Console()
console.builtins_hook()
console.logger_hook()
console.add_command("stop", console.stop, "stop - Just shutting down the server.\nUsage: stop", "Server shutdown.")
console.add_command("exit", console.stop, "stop - Just shutting down the server.\nUsage: stop", "Server shutdown.")


# Dirs
if not os.path.exists("mods"):
    os.mkdir("mods")
if not os.path.exists("plugins"):
    os.mkdir("plugins")

log.info(i18n.init)
