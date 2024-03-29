#!/usr/bin/python
# -*- coding=utf-8 -*-
import logging
import logging.handlers


def get_monitor_logger(logger_name):
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    log_file = '../log/monitor.log'
    fh = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=40
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


def mq_logger(logger_name):
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    log_file = '../log/%s.log' % logger_name
    fh = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=40
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


def offline_script_logger(logger_name):
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    log_file = '../log/%s.log' % logger_name
    fh = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1, backupCount=40
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    return logger


monitor_logger = get_monitor_logger("monitor")
