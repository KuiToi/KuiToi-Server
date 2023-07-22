Sure, here's a translation of the text:

# Passed Classes

## Worth looking at

1. What are `*args` and `**kwargs`? -> [Post on Habr (RU)](https://habr.com/ru/companies/ruvds/articles/482464/)

## KuiToi 
_`kt = KuiToi("PluginName"")`_

### kt.log
_Constant_\
Returns a pre-configured logger

### kt.name
_Constant_\
Returns the name of the plugin

### kt.dir
_Constant_\
Returns the directory of the plugin

### kt.open()
_Parameters are the same as for open()_\
Opens a file in kt.dir

### kt.register_event(event_name: str, event_func: function)
_`event_name: str` -> The name of the event that `event_func` will be called on._\
_`event_func: function` -> The function that will be called._

In `event_func`, you can pass both regular functions and async functions - you don't need to make them async beforehand.\
You can also create your own events with your own names.\
You can register an unlimited number of events.

### kt.call_event(event_name: str, *args, **kwargs) -> list:
_`event_name: str` -> The name of the event to call._\
_`*args, **kwargs` -> Arguments to be passed to the function._

### **async** kt.call_async_event(event_name: str, *args, **kwargs) -> list:
_`event_name: str` -> The name of the event to call._\
_`*args, **kwargs` -> Arguments to be passed to the function._\
_Must be called with `await`_

###### _I recommend familiarizing yourself with *args, **kwargs_, there is a link at the beginning
Data is passed to all events in the form of: `{"event_name": event_name, "args": args, "kwargs": kwargs}`\
`args: list` -> Represents an array of data passed to the event\
`kwargs: dict` -> Represents a dictionary of data passed to the event
The data will be returned from all successful attempts in an array.

### kt.call_lua_event(event_name: str, *args) -> list:
_`event_name: str` -> The name of the event to call._\
_`*args` -> Arguments to be passed to the function._

Added to support backward compatibility.\
The lua function is called with a direct transmission of arguments `lua_func(*args)`

### kt.get_player([pid: int], [nick: str]) -> Player | None:
_`pid: int` -> Player ID - The identifier of the player._\
_`nick: str` -> Player Nickname - The name of the player._

The method returns a player object by their `pid` or `nick`.\
If the player cannot be found, `None` will be returned.

### kt.get_players() -> List[Player] | list:

The method returns an array with all players.\
The array will be empty if there are no players.

### kt.players_counter() -> int:

The method returns the number of players currently online.

### kt.is_player_connected([pid: int], [nick: str]) -> bool:
_`pid: int` -> Player ID - The identifier of the player._\
_`nick: str` -> Player Nickname - The name of the player._

The method returns a player object by their `pid` or `nick`.

## Player (or Client) 
_`pl = kt.get_player()`_\
_`pl = event_data['kwargs']['player']`_

### pl.log -> Logger
_Constant_\
Returns a pre-configured logger

### pl.addr -> str
_Constant_\
Returns the IP address of the player

### pl.pid -> int
### pl.cid -> int
_Constant_\
Returns the client ID _(pid: PlayerId = cid: ClientId)_

### pl.key -> str
_Constant_\
Returns the key passed during authentication

### pl.nick -> str
_Variable_\
The nickname passed during authentication from the BeamMP server, can be changed, consequences are untested

### pl.roles -> str
_Variable_\
The role passed during authentication from the BeamMP server, can be changed (if an incorrect role is set, unexpected things may happen.)

### pl.guest -> bool
_Constant_\
Returns whether the player is a guest, passed during authentication from the BeamMP server

### pl.identifiers -> dict
_Constant_\
Identifiers passed during authentication from the BeamMP server.

### pl.ready -> bool
_Constant, changed by the core_\
Returns a bool value, if True -> the player has downloaded all resources, loaded on the map

### pl.cars -> dict
_Constant, changed by the core_\
Returns a dictionary of cars like thisSure, here's the translation:

# Passed Classes

## Worth looking at

1. What are `*args` and `**kwargs`? -> [Post on Habr ↗](https://habr.com/ru/companies/ruvds/articles/482464/)

## KuiToi 
_`kt = KuiToi("PluginName"")`_

### kt.log
_Constant_\
Returns a pre-configured logger

### kt.name
_Constant_\
Returns the name of the plugin

### kt.dir
_Constant_\
Returns the directory of the plugin

### kt.open()
_Parameters are the same as for open()_\
Opens a file in kt.dir

### kt.register_event(event_name: str, event_func: function)
_`event_name: str` -> The name of the event that `event_func` will be called on._\
_`event_func: function` -> The function that will be called._

In `event_func`, you can pass both regular functions and async functions - you don't need to make them async beforehand.\
You can also create your own events with your own names.\
You can register an unlimited number of events.

### kt.call_event(event_name: str, *args, **kwargs) -> list:
_`event_name: str` -> The name of the event to call._\
_`*args, **kwargs` -> Arguments to be passed to the function._

### **async** kt.call_async_event(event_name: str, *args, **kwargs) -> list:
_`event_name: str` -> The name of the event to call._\
_`*args, **kwargs` -> Arguments to be passed to the function._\
_Must be called with `await`_

###### _I recommend familiarizing yourself with *args, **kwargs_, there is a link at the beginning
Data is passed to all events in the form of: `{"event_name": event_name, "args": args, "kwargs": kwargs}`\
`args: list` -> Represents an array of data passed to the event\
`kwargs: dict` -> Represents a dictionary of data passed to the event
The data will be returned from all successful attempts in an array.

### kt.call_lua_event(event_name: str, *args) -> list:
_`event_name: str` -> The name of the event to call._\
_`*args` -> Arguments to be passed to the function._

Added to support backward compatibility.\
The lua function is called with a direct transmission of arguments `lua_func(*args)`

### kt.get_player([pid: int], [nick: str]) -> Player | None:
_`pid: int` -> Player ID - The identifier of the player._\
_`nick: str` -> Player Nickname - The name of the player._

The method returns a player object by their `pid` or `nick`.\
If the player cannot be found, `None` will be returned.

### kt.get_players() -> List[Player] | list:

The method returns an array with all players.\
The array will be empty if there are no players.

### kt.players_counter() -> int:

The method returns the number of players currently online.

### kt.is_player_connected([pid: int], [nick: str]) -> bool:
_`pid: int` -> Player ID - The identifier of the player._\
_`nick: str` -> Player Nickname - The name of the player._

The method returns a player object by their `pid` or `nick`.

## Player (or Client) 
_`pl = kt.get_player()`_\
_`pl = event_data['kwargs']['player']`_

### pl.log -> Logger
_Constant_\
Returns a pre-configured logger

### pl.addr -> str
_Constant_\
Returns the IP address of the player

### pl.pid -> int
### pl.cid -> int
_Constant_\
Returns the client ID _(pid: PlayerId = cid: ClientId)_

### pl.key -> str
_Constant_\
Returns the key passed during authentication

### pl.nick -> str
_Variable_\
The nickname passed during authentication from the BeamMP server, can be changed, consequences are untested

### pl.roles -> str
_Variable_\
The role passed during authentication from the BeamMP server, can be changed (if an incorrect role is set, unexpected things may happen.)

### pl.guest -> bool
_Constant_\
Returns whether the player is a guest, passed during authentication from the BeamMP server

### pl.identifiers -> dict
_Constant_\
Identifiers passed during authentication from the BeamMP server.

### pl.ready -> bool
_Constant, changed by the core_\
Returns a bool value, if True -> the player has downloaded all resources, loaded on the map

### pl.cars -> dict
_Constant, changed by the core_\
Returns a dictionary of cars like this