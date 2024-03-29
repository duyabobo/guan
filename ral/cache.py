#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 二级缓存
import copy
import pickle
import re

from util.log import monitor_logger
from util.redis_conn import redisConn


def checkInconsistentCache(prefix, ex=60):
    """允许不一致数据的缓存（不需要配套deleteCache"""
    def wrap(fn):
        def __inner__(*args, **kwargs):
            key = "%s:%s:%s:%s" % (prefix, fn.__name__, str(args), str(kwargs))
            val = redisConn.get(key)
            if val is not None:  # 缓存查询到数据
                ret = pickle.loads(val)
            else:
                ret = fn(*args, **kwargs)
                val = pickle.dumps(ret)
                redisConn.set(key, val, ex=ex)
            return ret
        return __inner__
    return wrap


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
    """
    需要一致性要求的缓存，需要配套deleteCache使用。
    要求：key必须使用显示format表示的字符串，比如 prefix:{arg1}:{args}，被用到的arg1也必须是关键字参数传递，或者能够从 self里获取（即args[0])
    """
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


def deleteCache(keys):
    """要求：key必须使用显示format表示的字符串，比如 prefix:{arg1}:{args}，被用到的arg1也必须是关键字参数传递，或者能够从 self里获取（即args[0])"""
    def wrap(fn):
        def __inner__(*args, **kwargs):
            for key in keys:
                cacheKey = getCacheKey(key, *args, **kwargs)
                if cacheKey:
                    redisConn.delete(cacheKey)
            return fn(*args, **kwargs)
        return __inner__
    return wrap
