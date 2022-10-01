#!/usr/bin/python3
import argparse
import asyncio

try:
    from modules.console.src.console import Console, ConsoleIO
except ImportError:
    Console, ConsoleIO = None, None
    print("Clone with submodules!")
    exit(1)

import __version__
import config_provider
import utils

parser = argparse.ArgumentParser(description='KuiToi-Server - BeamingDrive server compatible with BeamMP clients!')
parser.add_argument('-v', '--version', action="store_true", help='Print version and exit.', default=False)
parser.add_argument('--config', help='Patch to config file.', nargs='?', default=None, type=str)
log = utils.get_logger("main")
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
console = Console(prompt_out=":", async_loop=loop)


def init():
    global log
    log.info("Hello from KuiToi-Server!")
    args = parser.parse_args()
    if args.version:
        print(f"KuiToi-Server:\n\tVersion: {__version__.__version__}\n\tBuild: {__version__.__build__}")
        exit(0)

    config_patch = "kuitoi.yml"
    if args.config:
        config_patch = args.config
    log.info(f"Use {config_patch} for config.")

    cp = config_provider.ConfigProvider(config_patch)
    config = cp.open_config()
    if config.Server['debug'] is True:
        utils.set_debug_status()
        log.info("Getting new loggen with DEBUG level!")
        log = utils.get_logger("main")
        log.debug("Debug mode enabled!")
        log.debug(f"Server config: {config}")
    console.builtins_hook()
    console.logger_hook()


def start():
    tasks = [
        loop.create_task(console.async_run()),
    ]

    loop.run_until_complete(asyncio.wait(tasks))


def end():
    log.info("Goodbye!")


if __name__ == '__main__':
    init()
    try:
        start()
    except KeyboardInterrupt:
        print("Exiting..")
    end()
