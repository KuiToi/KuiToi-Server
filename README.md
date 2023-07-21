# KuiToi-Server

## About
**_[Status: Beta]_** \
BeamingDrive Multiplayer (BeamMP) server compatible with BeamMP clients.

## TODOs

- [x] Server core
  - [x] BeamMP System:
    - [x] Private access (Without key, Direct connect)
    - [x] Public access  (With key, listing in Launcher)
    - [X] Player authentication
  - [x] TCP Server part:
    - [x] Handle code
    - [x] Understanding BeamMP header
    - [x] Upload mods
    - [x] Connecting to the world
    - [x] Chat
    - [x] Players online counter
    - [x] Packets handled (Recursive finding second packet)
    - [ ] Client events
    - [x] Car synchronizations:
      - [x] State packets
      - [x] Spawn cars
      - [x] Delete cars
      - [x] Edit cars
      - [x] Reset cars
    - [x] "ABG:" (compressed data)
      - [x] Decompress data
      - [x] Compress data
  - [x] UDP Server part:
    - [x] Ping
    - [x] Position synchronizations
- [x] Additional:
  - [ ] KuiToi System
    - [ ] Servers counter
    - [ ] Players counter
    - [ ] Etc.
  - [x] Logger
    - [x] Just logging
    - [x] Log in file
    - [x] Log history (.1.log, .2.log, ...)
  - [x] Console:
    - [x] Tabulation
    - [x] History
    - [x] Autocomplete
  - [x] Events System
    - [x] Call events
    - [x] Create custom events
    - [x] Return from events
    - [x] Async support
    - [ ] Add all events
  - [x] Plugins support
    - [ ] Python part:
      - [x] Load Python plugins
      - [x] Async support
      - [ ] KuiToi class
      - [ ] Client (Player) class
    - [ ] JavaScript part:
      - [ ] Load JavaScript plugins
      - [ ] KuiToi class
      - [ ] Client (Player) class
    - [ ] Lua part: (Original BeamMP compatibility)
      - [x] Load Lua plugins
      - [x] MP Class (Excluding CreateEventTimer, CreateEventTimer, TriggerClientEventJson)
      - [ ] Util class
      - [x] FS class
  - [x] MultiLanguage (i18n support)
    - [ ] Core
    - [x] Console
    - [x] WebAPI
  - [ ] HTTP API Server (fastapi)
    - [x] Stop and Start with core
    - [x] Configure FastAPI logger
    - [ ] Sync with event system
    - [ ] Add methods...
- [ ] [Documentation](./docs/)

## Installation

1. Install **Python 3.10**
2. Clone the repository in a location of your choice with: `git clone -b Stable https://github.com/kuitoi/kuitoi-Server.git`.
3. Change directory into the KuiToi-Server: `cd KuiToi-Server`.
4. Install requirements: `pip install -r requirements.txt`.
5. Change directory into sources: `cd src`.
6. Run KuiToi-Server: `python3 main.py`.

## Feedback

If you have any questions, or you want to help the author in any way, you can write to him in \
Telegram: [@SantaSpeen](https://t.me/SantaSpeen) \
Discord: [SantaSpeen](https://discordapp.com/users/910990039557767241)

<br/>

## Licence
```text
Copyright (c) 2023 SantaSpeen (Maxim Khomutov)
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without limitation in the rights to use, copy, modify, merge, publish, and/ or distribute copies of the Software in an educational or personal context, subject to the following conditions:
- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
Permission is granted to sell and/ or distribute copies of the Software in a commercial context, subject to the following conditions:
- Substantial changes: adding, removing, or modifying large parts, shall be developed in the Software. Reorganizing logic in the software does not warrant a substantial change and received permission from the owner.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
