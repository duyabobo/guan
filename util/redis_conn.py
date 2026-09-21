#! /usr/bin/env python
# -*- coding: utf-8 -*-
from redis import StrictRedis
import util.config

redisConn = StrictRedis(util.config.get('redis', 'host'), util.config.get('redis', 'port'))


def decode_redis_value(value):
    """StrictRedis 默认返回 bytes，统一解码为 str 供业务比较/拼接。"""
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value
