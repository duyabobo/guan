#! /usr/bin/env python
# -*- coding: utf-8 -*-
from redis import StrictRedis
import util.config

REDIS_CONNECT_TIMEOUT_SEC = 2
REDIS_SOCKET_TIMEOUT_SEC = 3  # 同步调用跑在 IOLoop 上，Redis 一旦卡住没有超时就会拖死所有请求
REDIS_HEALTH_CHECK_INTERVAL_SEC = 30


def _build_redis():
    password = util.config.get_optional('redis', 'password')
    return StrictRedis(
        host=util.config.get('redis', 'host'),
        port=int(util.config.get('redis', 'port')),
        password=password or None,
        socket_connect_timeout=REDIS_CONNECT_TIMEOUT_SEC,
        socket_timeout=REDIS_SOCKET_TIMEOUT_SEC,
        health_check_interval=REDIS_HEALTH_CHECK_INTERVAL_SEC,
    )


redisConn = _build_redis()


def decode_redis_value(value):
    """StrictRedis 默认返回 bytes，统一解码为 str 供业务比较/拼接。"""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value
