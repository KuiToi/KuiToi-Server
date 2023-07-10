import BEAMP  # Import server object

beam = BEAMP("TestPlugin")  # Init plugin with name "TestPlugin"
log = beam.log  # Use logger from server


def on_load():
    # When plugin initialization Server uses plugin.load() to load plugin.
    # def load(): is really needed
    log.info(beam.name)


# Events handlers

def on_started():
    # Simple event handler
    log.info("Server starting...")


# Simple event register
beam.register_event("on_started", on_started)


def any_func(data=None):
    # Custom event handler
    log.info(f"Data from any_func: {data}")


# Create custom event
beam.register_event("my_event", any_func)

# Call custom event
beam.call_event("my_event")
beam.call_event("my_event", "Some data")
# This will be an error since any_func accepts only one argument at the input
beam.call_event("my_event", "Some data", "Some data1")
