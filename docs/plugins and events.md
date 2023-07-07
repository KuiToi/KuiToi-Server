# Plugins System

## Install

[//]: # (TODO: BEAM LIB)
Lib can't ready to use
* From pip:\
    `$ pip install ...`
* From source:\
    `git clone https://github.com/kuitoi/...`

## Example

```python
import BEAMP

beam = BEAMP("TestPlugin")
logger = beam.log

def load():  # Plugins load from here
    print(beam.name)

def on_started():
    logger.info("Server starting...")

beam.register_event("on_started", on_started)
```

* Basic Events: ['on_started', 'on_auth, 'on_stop']
* Create new event : `beam.register_event("my_event", my_event_function)`
* Call event: `beam.call_event("my_event")`
* Call event with some data: `beam.call_event("my_event", data, data2)`
* Calls _**can't support**_ like this: `beam.call_event("my_event", data=data)`
