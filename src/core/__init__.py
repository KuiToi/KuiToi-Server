# Developed by KuiToi Dev
# File core.__init__.py
# Written by: SantaSpeen
# Version 1.2
# Licence: FPA
# (c) kuitoi.su 2023
# Special thanks to: AI Sage(https://poe.com/Sage), AI falcon-40b-v7(https://OpenBuddy.ai)

__title__ = 'KuiToi-Server'
__description__ = 'BeamingDrive Multiplayer server compatible with BeamMP clients.'
__url__ = 'https://github.com/kuitoi/kuitoi-Server'
__version__ = '0.1.6'
__build__ = 458
__author__ = 'SantaSpeen'
__author_email__ = 'admin@kuitoi.su'
__license__ = "FPA"
__copyright__ = 'Copyright 2023 © SantaSpeen (Maxim Khomutov)'

import asyncio
import builtins
import os
import webbrowser

import prompt_toolkit.shortcuts as shortcuts

from .utils import get_logger
from core.core import Core
from main import parser
from modules import ConfigProvider, EventsSystem, PluginsLoader
from modules import Console
from modules import MultiLanguage

args = parser.parse_args()
if args.version:
    print(f"{__title__}:\n\tVersion: {__version__}\n\tBuild: {__build__}")
    exit(0)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
log = get_logger("core.init")

# Config file init
config_path = "kuitoi.yml"
if args.config:
    config_path = args.config
config_provider = ConfigProvider(config_path)
config = config_provider.open_config()
builtins.config = config
if config.Server['debug'] is True:
    utils.set_debug_status()
    log.info("Debug enabled!")
    log = get_logger("core.init")
    log.debug("Debug mode enabled!")
    log.debug(f"Server config: {config}")

# i18n init
log.debug("Initializing i18n...")
ml = MultiLanguage()
ml.set_language(args.language or config.Server['language'])
ml.builtins_hook()

log.debug("Initializing EventsSystem...")
ev = EventsSystem()
ev.builtins_hook()

log.info(i18n.hello)
log.info(i18n.config_path.format(config_path))

log.debug("Initializing BEAMP Server system...")
# Key handler..
if not config.Auth['private'] and not config.Auth['key']:
    log.warn(i18n.auth_need_key)
    url = "https://beammp.com/k/keys"
    if shortcuts.yes_no_dialog(
            title='BEAMP Server Key',
            text=i18n.GUI_need_key_message,
            yes_text=i18n.GUI_yes,
            no_text=i18n.GUI_no).run():
        try:
            log.debug("Opening browser...")
            webbrowser.open(url, new=2)
        except Exception as e:
            log.error(i18n.auth_cannot_open_browser.format(e))
            log.info(i18n.auth_use_link.format(url))
            shortcuts.message_dialog(
                title='BEAMP Server Key',
                text=i18n.GUI_cannot_open_browser.format(url),
                ok_text=i18n.GUI_ok).run()

    config.Auth['key'] = shortcuts.input_dialog(
        title='BEAMP Server Key',
        text=i18n.GUI_enter_key_message,
        ok_text=i18n.GUI_ok,
        cancel_text=i18n.GUI_cancel).run()
    config_provider.save_config()
if not config.Auth['private'] and not config.Auth['key']:
    log.error(i18n.auth_empty_key)
    log.info(i18n.stop)
    exit(1)

# Console Init
log.debug("Initializing console...")
console = Console()
console.builtins_hook()
# console.logger_hook()
console.add_command("stop", console.stop, i18n.man_message_stop, i18n.help_message_stop)
console.add_command("exit", console.stop, i18n.man_message_exit, i18n.help_message_exit)

log.debug("Initializing PluginsLoader...")
if not os.path.exists("plugins"):
    os.mkdir("plugins")
pl = PluginsLoader("plugins")
pl.load_plugins()

builtins.B = 1
builtins.KB = B * 1024
builtins.MB = KB * 1024
builtins.GB = MB * 1024
builtins.TB = GB * 1024

log.info(i18n.init_ok)
