#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File main.py
# Written by: SantaSpeen
# Version 0.1.0
# Licence: FPA
# (c) kuitoi.su 2023
import argparse
import asyncio

from core import utils

parser = argparse.ArgumentParser(description='KuiToi-Server - BeamingDrive server compatible with BeamMP clients!')
parser.add_argument('-v', '--version', action="store_true", help='Print version and exit.', default=False)
parser.add_argument('--config', help='Patch to config file.', nargs='?', default=None, type=str)
log = utils.get_logger("main")
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

if __name__ == '__main__':
    import core

    try:
        core.start()
    except KeyboardInterrupt:
        print("Exiting..")
    core.stop()
