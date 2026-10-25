#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import logging
import time

from util.const.identity import RUNTIME_UNION_TTL_SEC, SESSION_KEY_PREFIX
from util.encode import generate_secret
from util.errors import RateLimitExceeded, ReplayDetected
from util.redis_conn import decode_redis_value, redisConn
from util.session_payload import session_payload

logger = logging.getLogger(__name__)

UNIQUE_EXP_KEY = 'unique:{accessToken}:{exp}'
# 限频按固定窗口计数：窗口编号写进键里，窗口换了键自然换，不依赖"有没有设上过期"
FAILED_CNT_KEY = 'failed_cnt:{remote_ip}:{window}'
SUCCESS_CNT_KEY = 'success_cnt:{accessToken}:{window}'
RATE_WINDOW_SEC = 60
RATE_KEY_TTL_SEC = RATE_WINDOW_SEC * 2
UNIQUE_REQUEST_TTL_SEC = 60
FAILED_CNT_LIMIT_ONE_MINUTE = 60
SUCCESS_CNT_LIMIT_ONE_MINUTE = 300


def getLoginKey(accessToken):
    """
    返回登录查询 redis 的 key
    :return:
    """
    return SESSION_KEY_PREFIX + accessToken


def putSession(accessToken, passport_id):
    """
    把当前登录用户的基本信息放到 redis, 如果 redis 已有记录, 就更新, 如果没有, 就新增
    :param accessToken:
    :return:
    """
    secret = generate_secret(accessToken)  # 签名校验的密钥
    currentUserInfoJson = session_payload(passport_id, secret)
    loginKey = getLoginKey(accessToken)
    pipe = redisConn.pipeline()
    pipe.hset(loginKey, mapping=currentUserInfoJson)
    pipe.expire(loginKey, RUNTIME_UNION_TTL_SEC)
    pipe.execute()
    return secret


def delSession(accessToken):
    """
    删除登录的用户信息
    :param accessToken:
    :return:
    """
    redisConn.delete(getLoginKey(accessToken))


def _decode_redis_hash(raw):
    if not raw:
        return {}
    decoded = {}
    for key, value in raw.items():
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        decoded[key] = value
    return decoded


def getSession(accessToken):
    """
    从 redis 获取当前登录用户的信息
    :param accessToken:
    :return:
    """
    return _decode_redis_hash(redisConn.hgetall(getLoginKey(accessToken)))


def checkUnique(accessToken, requestSeq):
    """同一令牌的同一请求序号在有效期内只能出现一次。"""
    key = UNIQUE_EXP_KEY.format(accessToken=accessToken, exp=requestSeq)
    if not redisConn.set(key, 1, nx=True, ex=UNIQUE_REQUEST_TTL_SEC):
        raise ReplayDetected('request seq reused')


def _window_key(template, **fields):
    return template.format(window=int(time.time() // RATE_WINDOW_SEC), **fields)


def _incr_in_window(key):
    """计数加一，并保证这个键一定带过期时间。一次往返。"""
    pipe = redisConn.pipeline()
    pipe.incr(key)
    pipe.expire(key, RATE_KEY_TTL_SEC)
    count, _ = pipe.execute()
    return count


def _count_in_window(key):
    return int(decode_redis_value(redisConn.get(key)) or 0)


def setFailCnt(remote_ip):
    """失败请求处理"""
    _incr_in_window(_window_key(FAILED_CNT_KEY, remote_ip=remote_ip))


def setSuccessCnt(accessToken):
    """成功请求处理"""
    _incr_in_window(_window_key(SUCCESS_CNT_KEY, accessToken=accessToken))


def checkFailedCnt(remote_ip):
    """失败频次检查"""
    failed_cnt = _count_in_window(_window_key(FAILED_CNT_KEY, remote_ip=remote_ip))
    if failed_cnt >= FAILED_CNT_LIMIT_ONE_MINUTE:
        logger.warning("失败请求过于频繁 remote_ip=%s count=%s", remote_ip, failed_cnt)
        raise RateLimitExceeded('failed too frequent')


def checkSuccessCnt(accessToken):
    """成功频次检查。超限只拒绝，不清计数，窗口内持续有效。"""
    success_cnt = _count_in_window(_window_key(SUCCESS_CNT_KEY, accessToken=accessToken))
    if success_cnt > SUCCESS_CNT_LIMIT_ONE_MINUTE:
        logger.warning("成功请求过于频繁 count=%s", success_cnt)
        raise RateLimitExceeded('success too frequent')
