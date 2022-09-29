import logging
import os

log_format = "[%(asctime)s | %(name)s | %(levelname)-5s] %(message)s"
log_file = "server.log"
log_level = logging.INFO
# Инициализируем логирование
logging.basicConfig(level=log_level, format=log_format)
# Настройка логирование в файл.
if os.path.exists(log_file):
    os.remove(log_file)
fh = logging.FileHandler(log_file)
fh.setLevel(log_level)
fh.setFormatter(logging.Formatter(log_format))


def get_logger(name):
    log = logging.getLogger(name=name)
    log.addHandler(fh)
    return log


def set_debug_status():
    global log_level
    log_level = logging.DEBUG
