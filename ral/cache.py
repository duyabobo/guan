#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 二级缓存
import pickle

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


def get_cache_key(key, **kwargs):
    try:
        return key.format(**kwargs)
    except:
        return None


def checkCache(key, ex=3600):
    """
    需要一致性要求的缓存，需要配套deleteCache使用。
    要求：key必须使用显示format表示的字符串，比如 prefix:{arg1}:{args}，被用到的arg1也必须是关键字参数传递。
    """
    def wrap(fn):
        def __inner__(*args, **kwargs):
            cache_key = get_cache_key(key, **kwargs)
            if cache_key:
                val = redisConn.get(cache_key)
                if val is not None:  # 缓存查询到数据
                    return pickle.loads(val)

            ret = fn(*args, **kwargs)
            val = pickle.dumps(ret)
            if cache_key:
                redisConn.set(cache_key, val, ex=ex)
            return ret
        return __inner__
    return wrap


def deleteCache(keys):
    """要求：key必须使用显示format表示的字符串，比如 prefix:{arg1}:{args}，被用到的arg1也必须是关键字参数传递。"""
    def wrap(fn):
        def __inner__(*args, **kwargs):
            for key in keys:
                cache_key = get_cache_key(key, **kwargs)
                if cache_key:
                    redisConn.delete(cache_key)
            return fn(*args, **kwargs)
        return __inner__
    return wrap
