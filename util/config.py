#!/usr/bin/python
# -*- coding=utf-8 -*-
import logging
import os
from configparser import RawConfigParser

logger = logging.getLogger(__name__)


def singleton(cls):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class Configuration:
    def __init__(self, config_file=None):
        conf_name = os.getenv('CONFNAME') or 'du'
        default_conf = f"{conf_name}.conf"
        self._config_file = default_conf if not config_file else config_file
        self._load()

    def _load(self):
        self._config = RawConfigParser()
        logger.info("load config from %s", self._config_file)
        self._config.read(self._config_file)

    def get(self, sect, opt):
        return self._config.get(sect, opt)

    def get_section(self, section):
        if not self._config.has_section(section):
            return {}
        items = self._config.items(section)
        return dict(items)


def get(sect, opt):
    return Configuration().get(sect, opt)


def get_section(sect):
    return Configuration().get_section(sect)


def get_conf(key: str, default: str = '') -> str:
    """
    读取扁平配置项（适用于 LLM 等第三方服务的 key）。
    查找顺序：
      1. 环境变量（key 转大写，如 openai_api_key → OPENAI_API_KEY）
      2. INI 文件 [llm] section（key 原名）
      3. 返回 default
    """
    env_val = os.getenv(key.upper())
    if env_val is not None:
        return env_val
    try:
        return Configuration().get('llm', key)
    except Exception:
        return default
