#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 二级缓存和分布式锁
import copy
import functools
import json
import logging
import re
import uuid

from util.redis_conn import redisConn

logger = logging.getLogger(__name__)

LOCK_DEFAULT_TTL_SEC = 10
CACHE_DEFAULT_TTL_SEC = 3600

# 只有锁还是自己的才删除。锁超时被别人拿走后，原持有者不能把别人的锁误删。
_RELEASE_LOCK_LUA = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""
_release_lock_script = redisConn.register_script(_RELEASE_LOCK_LUA)


def getCacheKey(key, *args, **kwargs):
    _self = args[0]
    params = re.split('[{}]', key)
    _kwargs = copy.deepcopy(kwargs)
    for p in params:
        if hasattr(_self, p):
            _kwargs[p] = getattr(_self, p)
    try:
        return key.format(**_kwargs)
    except (KeyError, IndexError, ValueError):
        logger.exception("缓存键拼装失败 key=%s", key)
        return None


def lock(key, failRet=None, ex=LOCK_DEFAULT_TTL_SEC):
    """分布式锁。抢不到或键拼不出来，直接返回 failRet；持有者异常退出也会释放。"""
    def wrap(fn):
        @functools.wraps(fn)
        def __inner__(*args, **kwargs):
            cacheKey = getCacheKey(key, *args, **kwargs)
            if not cacheKey:
                return failRet
            owner_token = uuid.uuid4().hex
            if not redisConn.set(cacheKey, owner_token, nx=True, ex=ex):
                logger.info("抢锁失败 key=%s", cacheKey)
                return failRet
            try:
                return fn(*args, **kwargs)
            finally:
                if not _release_lock_script(keys=[cacheKey], args=[owner_token]):
                    logger.warning("锁释放时已不属于自己，可能执行超过 ttl key=%s ttl=%s", cacheKey, ex)
        return __inner__
    return wrap


def checkCache(key, ex=CACHE_DEFAULT_TTL_SEC):
    """读缓存。key 用 format 占位，参数来自关键字或 self 属性。值只允许 JSON 可表示的类型。"""
    def wrap(fn):
        @functools.wraps(fn)
        def __inner__(*args, **kwargs):
            forceRefreshCache = kwargs.pop("forceRefreshCache", False)  # 缓存层自己消化，被装饰函数不必声明这个参数
            cacheKey = getCacheKey(key, *args, **kwargs)
            if cacheKey and not forceRefreshCache:
                hit, cached = _read_cache(cacheKey)
                if hit:
                    return cached

            ret = fn(*args, **kwargs)
            if cacheKey:
                _write_cache(cacheKey, ret, ex)
            return ret
        return __inner__
    return wrap


def _read_cache(cache_key):
    raw = redisConn.get(cache_key)
    if raw is None:
        return False, None
    try:
        return True, json.loads(raw)
    except ValueError:  # 含 UnicodeDecodeError。旧版本写入的 pickle 也会走到这里，按未命中处理
        logger.warning("缓存内容不是 JSON，按未命中处理 key=%s", cache_key)
        return False, None


def _write_cache(cache_key, value, ttl_sec):
    try:
        payload = json.dumps(value)
    except TypeError:
        logger.error("缓存值不是 JSON 可表示类型，未写入 key=%s type=%s", cache_key, type(value).__name__)
        return
    redisConn.set(cache_key, payload, ex=ttl_sec)
