# Developed by KuiToi Dev
# File core.utils.py
# Written by: SantaSpeen
# Version 1.0
# Licence: FPA
# (c) kuitoi.su 2023

import logging

log_format = "[%(asctime)s | %(name)-14s | %(levelname)-5s] %(message)s"
log_format_access = '[%(asctime)s | %(name)-14s | %(levelname)-5s] %(client_addr)s - "%(request_line)s" %(status_code)s'
log_file = "server.log"
log_level = logging.INFO
# Инициализируем логирование
logging.basicConfig(level=log_level, format=log_format)
# Настройка логирование в файл.
# if os.path.exists(log_file):
#     os.remove(log_file)
fh = logging.FileHandler(log_file, encoding='utf-8')
fh.setFormatter(logging.Formatter(log_format))


def get_logger(name):
    log = logging.getLogger(name=name)
    log.addHandler(fh)
    log.level = log_level
    log.handlers[0].level = log_level
    return log


def set_debug_status():
    global log_level
    log_level = 10
