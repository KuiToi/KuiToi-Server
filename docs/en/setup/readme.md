# Greetings from KuiToi Server

## Well, let's begin

###### _(Here are the commands for Linux)_

* **Python 3.10.x** is required to run the server! It won't work on Python 3.11...
* You can check the version of your Python installation with the following command:
```bash
python3 --version  # Python 3.10.6
```
* Clone the repository and navigate to it.
* Install everything that's needed.
* Then, using my "script", remove all unnecessary files and move to the core source code.
```bash
git clone -b Stable https://github.com/kuitoi/KuiToi-Server.git && cd KuiToi-Server
pip install -r requirements.txt
mv ./src/ $HOME/ktsrc/ && rm -rf ./* && mv $HOME/ktsrc/* . && rm -rf $HOME/ktsrc
```
* Here's how to view information about the server and start it:
```bash
python3 main.py --help  # Displays all available commands
python3 main.py # Starts the server
```

## Configuration

* After starting the server, a `kuitoi.yaml` file will be created.
* By default, it looks like this:
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
  debug: false
  description: Welcome to KuiToi Server!
  language: en
  name: KuiToi-Server
  server_ip: 0.0.0.0
  server_port: 30813
WebAPI:
  enabled: false
  secret_key: <random_key>
  server_ip: 127.0.0.1
  server_port: 8433

```
### Auth

* If you set `private: false` and do not set a `key`, the server will request a BeamMP key and will not start without it.
* By entering a BeamMP key, the server will appear in the launcher list.
* You can get a key here: [https://beammp.com/k/keys ↗](https://beammp.com/k/keys)

### Game

* `map` specifies only the name of the map. That is, open the mod with the map in `map.zip/levels` - the name of the map will be there, and that's what you need to insert.
* `max_cars` - the maximum number of cars per player
* `players` - the maximum number of players

### Server

* `debug` - should debug messages be displayed (for experienced users only; slightly affects performance)
* `description` - server description for the BeamMP launcher
* `language` - the language in which the server will run (currently available: en, ru)
* `name` - server name for the BeamMP launcher
* `server_ip` - the IP address to be used by the server (for experienced users only; defaults to 0.0.0.0)
* `server_port` - the port on which the server will run

### WebAPI
##### _Docs are not ready yet_