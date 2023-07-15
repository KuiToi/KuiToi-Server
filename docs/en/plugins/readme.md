# Plugin System

## Installing the Library with "Stubs"
###### (This means that it will not work without a server, but the IDE will suggest the API)
###### (The library is still under development)

* Using pip:\
    `$ pip install KuiToi`
* From source code:\
    `git clone https://github.com/KuiToi/KuiToi-PyLib`

## Example

```python
try:
    import KuiToi
except ImportError:
    pass

kt = KuiToi("Example")
log = kt.log

def my_event_handler(event_data):
    log.info(f"{event_data}")

def load():
    # Plugin initialization
    ev.register_event("my_event", my_event_handler)
    log.info("Plugin loaded successfully.")

    
def start():
    # Running plugin processes
    ev.call_event("my_event")
    ev.call_event("my_event", "Some data", data="some data too")
    log.info("Plugin started successfully.")


def unload():
    # Code that ends all processes
    log.info("Plugin unloaded successfully.")
```

* It is recommended to use `open()` after `load()`. Otherwise, use `kt.load()` - creates a file in the `plugin/<plugin_name>/<filename>` folder.
* Creating your own event: `kt.register_event("my_event", my_event_function)`
* Calling an event: `kt.call_event("my_event")`
* Calling an event with data: `kt.call_event("my_event", data, data2=data2)`
* Basic events: _Will write later_

## Async Functions

Async support is available.

```python
try:
    import KuiToi
except ImportError:
    pass

kt = KuiToi("Example")
log = kt.log


async def my_event_handler(event_data):
    log.info(f"{event_data}")


async def load():
    # Plugin initialization
    ev.register_event("my_event", my_event_handler)
    log.info("Plugin loaded successfully.")


async def start():
    # Running plugin processes
    await ev.call_async_event("my_event")
    await ev.call_async_event("my_event", "Some data", data="some data too")
    log.info("Plugin started successfully.")


async def unload():
    # Code that ends all processes
    log.info("Plugin unloaded successfully.")

```

A more extensive example can also be found in [async_example.py](./async_example.py).

* Creating your own event: `kt.register_event("my_event", my_event_function)` (register_event checks for function)
* Calling an async event: `kt.call_async_event("my_event")`
* Calling an async event with data: `kt.call_async_event("my_event", data, data2=data2)`
* Basic async events: _Will write later_