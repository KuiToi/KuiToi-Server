# Система плагинов

## Установка библиотеки с "Заглушками"
###### (Это значит, что не будет работать без сервера, но IDE подскажет API)
###### (Библиотека ещё в разработке)

* Используя pip:\
    `$ pip install KuiToi`
* Из исходников:\
    `git clone https://github.com/KuiToi/KuiToi-PyLib`

## Пример

```python
import KuiToi

beam = KuiToi("TestPlugin")
logger = beam.log

def load():  # Plugins load from here
    print(beam.name)

def on_started():
    logger.info("Server starting...")

beam.register_event("on_started", on_started)
```

Так же более обширный пример можно найти в [example.py](./example.py)

* Базовые ивенты: ['on_started', 'on_auth, 'on_stop']
* Создание своего ивента : `beam.register_event("my_event", my_event_function)`
* Вызов ивента: `beam.call_event("my_event")`
* Вызов ивента с данными: `beam.call_event("my_event", data, data2)`
* Вызовы с указанием переменой _**не поддерживаются**_: `beam.call_event("my_event", data=data)`
