# Developed by KuiToi Dev
# File core.core.py
# Written by: SantaSpeen
# Version 0.1.0
# Licence: FPA
# (c) kuitoi.su 2023
import asyncio

from core import utils

log = utils.get_logger("core")

loop = asyncio.get_event_loop()


def start():
    log.info("Start!")


def stop():
    log.info("Goodbye!")
