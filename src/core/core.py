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


async def main():
    log.info("Server started!")
    while True:
        await asyncio.sleep(1)


async def astart():
    tasks = [console.start(), main()]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)


def start():
    asyncio.run(astart())


def stop():
    log.info("Goodbye!")
