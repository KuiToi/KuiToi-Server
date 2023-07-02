#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File main.py
# Written by: SantaSpeen
# Version 1.0
# Licence: FPA
# (c) kuitoi.su 2023
import argparse

parser = argparse.ArgumentParser(description='KuiToi-Server - BeamingDrive server compatible with BeamMP clients!')
parser.add_argument('-v', '--version', action="store_true", help='Print version and exit.', default=False)
parser.add_argument('--config', help='Patch to config file.', nargs='?', default=None, type=str)

if __name__ == '__main__':
    from core import Core
    core = Core()
    try:
        core.start()
    except KeyboardInterrupt:
        pass
    finally:
        core.stop()
