import builtins

from core import get_logger


# noinspection PyShadowingBuiltins
class EventsSystem:

    def __init__(self):
        # TODO: default events
        self.__events = {
            "on_started": [],
            "auth_sent_key": [],
            "auth_ok": [],
            "chat_receive": [],
        }
        self.log = get_logger("EventsSystem")

    def builtins_hook(self):
        self.log.debug("used builtins_hook")
        builtins.ev = self

    def register_event(self, event_name, event_func):
        self.log.debug(f"register_event({event_name}, {event_func}):")
        if not callable(event_func):
            # TODO: i18n
            self.log.error(f"Cannot add event '{event_name}'. "
                           f"Use `KuiToi.add_event({event_name}', function)` instead. Skipping it...")
            return
        if event_name not in self.__events:
            self.__events.update({str(event_name): [event_func]})
        else:
            self.__events[event_name].append(event_func)

    def call_event(self, event_name, *args, **kwargs):
        self.log.debug(f"Using event '{event_name}'")
        funcs_data = []

        if event_name in self.__events.keys():
            for func in self.__events[event_name]:
                try:
                    funcs_data.append(func({"event_name": event_name, "args": args, "kwargs": kwargs}))
                except Exception as e:
                    # TODO: i18n
                    self.log.error(f'Error while calling "{event_name}"; In function: "{func.__name__}"')
                    self.log.exception(e)
        else:
            # TODO: i18n
            self.log.warning(f"Event {event_name} does not exist. Just skipping it...")

        return funcs_data
