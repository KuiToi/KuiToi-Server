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
  description: This server uses KuiToi!
  name: KuiToi-Server
  server_ip: 0.0.0.0
  server_port: 30814
```
* Если поставить `private: false` и не установить `key`, то сервер запросит BEAMP ключ, без него не запустится.
* Введя BEAMP ключ сервер появится в списке лаунчера.
* Взять ключ можно тут: [https://beammp.com/k/keys](https://beammp.com/k/keys)

