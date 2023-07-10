# Hello from KuiToi Server

## Start

* Need **Python 3.10.x** to start!
* After cloning use this:
```bash
$ python3 --version  # Python 3.10.6
$ python3 main.py --help  # Show help message
$ python3 main.py # Start server
```

## Setup

* After starting server creating `kuitoi.yaml`; Default:
```yaml
!!python/object:modules.ConfigProvider.config_provider.Config
Auth:
  key: null
  private: true
Game:
  map: gridmap_v2
  max_cars: 1
  players: 8
Server:
  debug: true
  description: This server uses KuiToi!
  name: KuiToi-Server
  server_ip: 0.0.0.0
  server_port: 30814
```
* Server can't start without BEAM Auth.key

