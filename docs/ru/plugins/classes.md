# Передаваемые классы

## Стоит ознакомится

1. Что такое `*args` и `**kwargs`? -> [Пост на habr](https://habr.com/ru/companies/ruvds/articles/482464/)

## KuiToi 
_`kt = KuiToi("PluginName"")`_

### kt.log
_Константа_\
Вернёт преднастроенный логгер

### kt.name
_Константа_\
Вернёт имя плагина

### kt.dir
_Константа_\
Вернёт папку плагина

### kt.open()
_Параметры как у open()_\
Открывает файл в kt.dir

### kt.register_event(event_name: str, event_func: function)
_`event_name: str` -> Имя ивента, по которому будет вызвана `event_func`._\
_`event_func: function` -> Функция, которая будет вызвана._

В `event_func` можно передавать как обычную функцию, так и async - await не нужно делать заранее.\
Ивенты можно создавать так же свои, со своим именем.\
Зарегистрировать можно не ограниченное кол-во ивентов.

### kt.call_event(event_name: str, *args, **kwargs) -> list:
_`event_name: str` -> Имя ивента, который будет вызван._\
_`*args, **kwargs` -> Аргументы, передаваемые во функции._

### **async** kt.call_async_event(event_name: str, *args, **kwargs) -> list:
_`event_name: str` -> Имя ивента, который будет вызван._\
_`*args, **kwargs` -> Аргументы, передаваемые во функции._\
_Необходимо вызывать с `await`_

###### _Советую ознакомиться с *args, **kwargs_, ссылка есть в начале
Данные во все ивенты приходят по типу: `{"event_name": event_name, "args": args, "kwargs": kwargs}`\
`args: list` -> Представляет из себя массив данных, которые переданы в ивент\
`kwargs: dict` -> Представляет из себя словарь данных, которые переданы в ивент
Данные вернутся от всех удачных волнений в массиве.

### kt.call_lua_event(event_name: str, *args) -> list:
_`event_name: str` -> Имя ивента, который будет вызван._\
_`*args` -> Аргументы, передаваемые во функции._

Добавлено для поддержки обратной совместимости.\
lua функция вызывается с прямой передачей аргументов `lua_func(*args)`

### kt.get_player([pid: int], [nick: str]) -> Player | None:
_`pid: int` -> Player ID - Идентификатор игрока._\
_`nick: str` -> Player Nick - Ник игрока._

Метод возвращает объект игрока по его `pid`, `nick`.\
Если не удалось найти игрока вернётся `None`.

### kt.get_players() -> List[Player] | list:

Метод возвращает массив со всеми игроками.\
Массив будет пустой, если игроков нет.

### kt.players_counter() -> int:

Метод возвращает количество игроков, которые сейчас онлайн.

### kt.is_player_connected([pid: int], [nick: str]) -> bool:
_`pid: int` -> Player ID - Идентификатор игрока._\
_`nick: str` -> Player Nick - Ник игрока._

Метод возвращает объект игрока по его `pid`, `nick`.

## Player (или Client) 
_`pl = kt.get_player()`_\
_`pl = event_data['kwargs']['player']`_\

#### pl.
