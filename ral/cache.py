#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 二级缓存
import pickle

from util.redis_conn import redisConn


def cache(prefix, ex=60):
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
