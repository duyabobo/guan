#!/usr/bin/python
# -*- coding=utf-8 -*-
import logging
import logging.handlers
import os

# 日志目录优先读取环境变量，默认为项目根目录下的 log/
LOG_DIR = os.getenv('LOG_DIR', os.path.join(os.path.dirname(__file__), '..', 'log'))
os.makedirs(LOG_DIR, exist_ok=True)


def _build_rotating_handler(log_file: str) -> logging.handlers.TimedRotatingFileHandler:
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=40
    )
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler


def get_monitor_logger(logger_name: str) -> logging.Logger:
    log_file = os.path.join(LOG_DIR, 'monitor.log')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_build_rotating_handler(log_file))
    return logger


def offline_script_logger(logger_name: str) -> logging.Logger:
    log_file = os.path.join(LOG_DIR, f'{logger_name}.log')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_build_rotating_handler(log_file))
    return logger


monitor_logger = get_monitor_logger("monitor")
