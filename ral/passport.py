#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import time

from util.encode import generate_secret
from util.redis_conn import redisConn

UNIQUE_EXP_KEY = 'unique:{accessToken}:{exp}'
FAILED_CNT_ONE_MINUTE = 'failed_cnt:one_minute:{remote_ip}'
SUCCESS_CNT_ONE_MINUTE = 'success_cnt:one_minute:{accessToken}'
FAILED_CNT_LIMIT_ONE_MINUTE = 60
SUCCESS_CNT_LIMIT_ONE_MINUTE = 300


def getLoginKey(accessToken):
    """
    返回登录查询 redis 的 key
    :return:
    """
    return 'accessToken:' + accessToken


def putSession(accessToken, passport):
    """
    把当前登录用户的基本信息放到 redis, 如果 redis 已有记录, 就更新, 如果没有, 就新增
    :param accessToken:
    :param passport:
    :return:
    """
    currentUserInfoJson = {
        "accessToken": accessToken,
        "secret": generate_secret(accessToken),  # 签名校验的密钥
        "success_cnt": 1,
        "success_from_time": time.time(),
    }
    currentUserInfoJson.update({
        k: passport.__dict__[k]
        for k in passport.__dict__
        if k in ['id', 'phone', 'openid']
    })
    loginKey = getLoginKey(accessToken)
    redisConn.hmset(loginKey, currentUserInfoJson)
    redisConn.expire(loginKey, 3*30*24*3600)
    return currentUserInfoJson


def delSession(accessToken):
    """
    删除登录的用户信息
    :param accessToken:
    :return:
    """
    redisConn.delete(getLoginKey(accessToken))


def getSession(accessToken):
    """
    从 redis 获取当前登录用户的信息
    :param accessToken:
    :return:
    """
    return redisConn.hgetall(getLoginKey(accessToken))


def checkUnique(accessToken, exp):
    key = UNIQUE_EXP_KEY.format(accessToken=accessToken, exp=exp)
    assert exp < time.time() + 60, 'exp is too big'
    ret = redisConn.set(key, 1, nx=True, ex=60)
    assert int(ret), 'set unique error'


def setFailCnt(remote_ip):
    """失败请求处理"""
    failed_key = FAILED_CNT_ONE_MINUTE.format(remote_ip=remote_ip)
    failed_cnt = redisConn.incr(failed_key)
    if failed_cnt < 10:  # 前十次都重置过期时间，防止某一次重置过期时间失败
        redisConn.expire(failed_key, 60)


def setSuccessCnt(accessToken):
    """成功请求处理"""
    success_cnt_key = SUCCESS_CNT_ONE_MINUTE.format(accessToken=accessToken)
    success_cnt = redisConn.incr(success_cnt_key)
    if success_cnt < 10:  # 前十次都重置过期时间，防止某一次重置过期时间失败
        redisConn.expire(success_cnt_key, 60)


def checkFailedCnt(remote_ip):
    """失败频次检查"""
    failed_key = FAILED_CNT_ONE_MINUTE.format(remote_ip=remote_ip)
    failed_cnt = redisConn.get(failed_key) or 0
    assert failed_cnt < FAILED_CNT_LIMIT_ONE_MINUTE, 'failed too frequent'


def checkSuccessCnt(accessToken):
    """成功频次检查"""
    success_cnt_key = SUCCESS_CNT_ONE_MINUTE.format(user_id=accessToken)
    success_cnt = redisConn.get(success_cnt_key) or 0
    if success_cnt > SUCCESS_CNT_LIMIT_ONE_MINUTE:
        redisConn.delete(success_cnt_key)
        raise Exception('success too frequent')
