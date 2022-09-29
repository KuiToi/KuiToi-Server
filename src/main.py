import argparse

import __version__
import config_provider

parser = argparse.ArgumentParser(description='KuiToi-Server - BeamingDrive server compatible with BeamMP clients!')
parser.add_argument('-v', '--version', action="store_true", help='Print version and exit.', default=False)
parser.add_argument('--config', help='Patch to config file.', nargs='?', default=None, type=str)


def main():
    args = parser.parse_args()
    if args.version:
        print(f"KuiToi-Server:\n\tVersion: {__version__.__version__}\n\tBuild: {__version__.__build__}")
        exit(0)

    config_patch = "kuitoi.yml"
    if args.config:
        config_patch = args.config
    cp = config_provider.ConfigProvider(config_patch)
    config = cp.open_config()
    print(config)


if __name__ == '__main__':
    main()
