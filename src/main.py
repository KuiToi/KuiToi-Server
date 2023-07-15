#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Developed by KuiToi Dev
# File main.py
# Written by: SantaSpeen
# Version 1.1
# Licence: FPA
# (c) kuitoi.su 2023
import argparse

parser = argparse.ArgumentParser(description='KuiToi-Server - BeamingDrive server compatible with BeamMP clients!')
parser.add_argument('-v', '--version', action="store_true", help='Print version and exit.', default=False)
parser.add_argument('--config', help='Patch to config file.', nargs='?', default=None, type=str)
parser.add_argument('--language', help='Setting localisation.', nargs='?', default=None, type=str)


def main():
    from core import Core
    try:
        Core().start()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
