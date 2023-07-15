# Привет из KuiToi Server

## Что ж, начнём

###### _(Тут команды для linux)_

* Для запуска необходим **Python 3.10.x**! Именно этот, на Python 3.11 не запустится...
* Проверить версию твоего питончика(здесь надо смеяться) можно вот так:
```bash
python3 --version  # Python 3.10.6
```
* Клонируем репозиторий и переходим в него
* Устанавливаем всё необходимое
* Далее, используя мой "скриптик" удаляем всё лишнее и перемещаемся к исходникам ядра
```bash
git clone -b Stable https://github.com/kuitoi/KuiToi-Server.git && cd KuiToi-Server
pip install -r requirements.txt
mv ./src/ $HOME/ktsrc/ && rm -rf ./* && mv $HOME/ktsrc/* . && rm -rf $HOME/ktsrc
```
* Вот так можно глянуть инфу о сервер и запустить его:)
```bash
python3 main.py --help  # Покажет все доступные команды
python3 main.py # Запустит сервер
```

## Настройка

* После запуска создастся `kuitoi.yaml`
* По умолчанию он выглядит вот так:
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

* Если поставить `private: false` и не установить `key`, то сервер запросит BeamMP ключ, без него не запустится.
* Введя BeamMP ключ сервер появится в списке лаунчера.
* Взять ключ можно тут: [https://beammp.com/k/keys](https://beammp.com/k/keys)

### Game

* `map` указывается только название карты, т.е. открываем мод с картой в `map.zip/levels` - вот тут будет название карты, его мы и вставляем
* `max_cars` - Максимальное количество машин на игрока
* `players` - Максимально количество игроков

### Server

* `debug` - Нужно ли выводить debug сообщения (только для опытных пользователей, немного теряется в производительности)
* `description` - Описания сервера для лаунчера BeamMP
* `language` - С каким языком запустится сервер (Доступные на данный момент: en, ru)
* `name` - Названия сервер для лаунчера BeamMP
* `server_ip` - Какой IP адрес занять серверу (только для опытных пользователей, по умолчанию 0.0.0.0)
* `server_port` - На каком порту будет работать сервер

### WebAPI
##### _Доки не готовы_

