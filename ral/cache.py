#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 二级缓存
import copy
import pickle
import re

from util.log import monitor_logger
from util.redis_conn import redisConn


def getCacheKey(key, *args, **kwargs):
    _self = args[0]
    params = re.split('[{}]', key)
    _kwargs = copy.deepcopy(kwargs)
    for p in params:
        if hasattr(_self, p):
            _kwargs[p] = getattr(_self, p)
    try:
        return key.format(**_kwargs)
    except Exception as e:
        monitor_logger.exception(e)
        return None


def lock(key, failRet=None, ex=10):
    """分布式锁"""
    def wrap(fn):
        def __inner__(*args, **kwargs):
            cacheKey = getCacheKey(key, *args, **kwargs)
            if redisConn.set(cacheKey, 1, nx=1, ex=ex):
                ret = fn(*args, **kwargs)
                redisConn.delete(cacheKey)
                return ret
            else:
                return failRet
        return __inner__
    return wrap


def checkCache(key, ex=3600):
    """读缓存。key 用 format 占位，参数来自关键字或 self 属性。"""
    def wrap(fn):
        def __inner__(*args, **kwargs):
            forceRefreshCache = kwargs.get("forceRefreshCache", False)
            cacheKey = getCacheKey(key, *args, **kwargs)
            if cacheKey and not forceRefreshCache:
                val = redisConn.get(cacheKey)
                if val is not None:  # 缓存查询到数据
                    try:
                        return pickle.loads(val)
                    except Exception as e:
                        monitor_logger.exception(e)

            ret = fn(*args, **kwargs)
            val = pickle.dumps(ret)
            if cacheKey:
                redisConn.set(cacheKey, val, ex=ex)
            return ret
        return __inner__
    return wrap
