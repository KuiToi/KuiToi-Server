# Developed by KuiToi Dev
# File core.__init__.py
# Written by: SantaSpeen
# Version 0.1.0
# Licence: FPA
# (c) kuitoi.su 2023

__title__ = 'KuiToi-Server'
__description__ = 'BeamingDrive Multiplayer server compatible with BeamMP clients.'
__url__ = 'https://github.com/kuitoi/kuitoi-Server'
__version__ = '0.1.0'
__build__ = 77
__author__ = 'SantaSpeen'
__author_email__ = 'admin@kuitoi.su'
__license__ = "FPA"
__copyright__ = 'Copyright 2023 © SantaSpeen (Maxim Khomutov)'

import asyncio
import os

from core import utils
from core.config_provider import ConfigProvider
from main import parser
from modules import Console
from core.core import start
from core.core import stop

loop = asyncio.get_event_loop()

console = Console()
log = utils.get_logger("init")

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
    utils.set_debug_status()
    log.info("Getting new loggen with DEBUG level!")
    log = utils.get_logger("main")
    log.debug("Debug mode enabled!")
    log.debug(f"Server config: {config}")
console.builtins_hook()
console.logger_hook()

if not os.path.exists("mods"):
    os.mkdir("mods")
if not os.path.exists("plugins"):
    os.mkdir("plugins")

log.info("Initializing ready.")
