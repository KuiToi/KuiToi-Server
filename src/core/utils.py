# Developed by KuiToi Dev
# File core.utils.py
# Written by: SantaSpeen
# Version 1.1
# Core version: 0.4.0
# Licence: FPA
# (c) kuitoi.su 2023
import datetime
import logging
import os
import tarfile

log_format = "[%(asctime)s | %(name)-14s | %(levelname)-5s] %(message)s"
log_dir = "./logs/"
log_file = log_dir + "server.log"
log_level = logging.INFO
# Инициализируем логирование
logging.basicConfig(level=log_level, format=log_format)
# Настройка логирование в файл.
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
if os.path.exists(log_file):
    ftime = os.path.getmtime(log_file)
    gz_path = log_dir + datetime.datetime.fromtimestamp(ftime).strftime('%d.%m.%Y') + "-%s.tar.gz"
    index = 1
    while True:
        if not os.path.exists(gz_path % index):
            break
        index += 1
    with tarfile.open(gz_path % index, "w:gz") as tar:
        logs_files = [log_file, "./logs/web.log", "./logs/web_access.log"]
        for file in logs_files:
            if os.path.exists(file):
                tar.add(file, os.path.basename(file))
                os.remove(file)
fh = logging.FileHandler(log_file, encoding="utf-8")
fh.setFormatter(logging.Formatter(log_format))


def get_logger(name):
    try:
        fh.encoding = config.enc
    except NameError:
        fh.encoding = "utf-8"
    log = logging.getLogger(name=name)
    log.addHandler(fh)
    log.level = log_level
    log.handlers[0].level = log_level
    return log


def set_debug_status():
    global log_level
    log_level = 10
