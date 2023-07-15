# KuiToi-Server

## About
**_[Status: Alpha]_** \
BeamingDrive Multiplayer (BeamMP) server compatible with BeamMP clients.

## TODOs

- [ ] Server core
  - [x] BeamMP System
    - [x] Private access (Without key, Direct connect)
    - [x] Public access  (With key, listing in Launcher)
    - [X] Player authentication
  - [ ] KuiToi System
    - [ ] Servers counter
    - [ ] Players counter
    - [ ] Etc.
  - [ ] TCP Server part:
    - [x] Handle code
    - [x] Understanding BeamMP header
    - [x] Upload mods
    - [x] Connecting to the world
    - [x] Chat
    - [x] Players online counter
    - [ ] Car state synchronizations _(Codes: We, Vi)_
    - [ ] "ABG:" (compressed data)
      - [x] Decompress data
      - [ ] Vehicle data _(Code: Os)_
  - [ ] UDP Server part:
    - [ ] Players synchronizations _(Code: Zp)_
    - [ ] Ping _(Code: p)_
- [x] Additional:
  - [x] Logger
    - [x] Just logging
    - [x] Log in file
    - [x] Log history (.1.log, .2.log, ...)
  - [x] Console:
    - [x] Tabulation
    - [ ] _(Deferred)_ Static text (bug)
  - [x] Events System
    - [x] Call events
    - [x] Create custom events
    - [x] Return from events
    - [x] Async support
  - [x] Plugins support
    - [ ] KuiToi class
    - [x] Load Python plugins
    - [x] Async support
    - [ ] Load Lua plugins (Original BeamMP compatibility)
  - [x] MultiLanguage (i18n support)
    - [x] Core
    - [x] Console
    - [x] WebAPI
  - [x] HTTP API Server (fastapi)
    - [x] Stop and Start with core
    - [x] Configure FastAPI logger
    - [ ] Sync with event system
    - [ ] Add methods...
- [ ] [Documentation](docs/en/readme.md)

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
