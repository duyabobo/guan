#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.redis_conn import redisConn


def getTokenKey():
    return "wx:miniprogram:accesstoken"


def getToken():
    key = getTokenKey()
    return redisConn.get(key)


def setToken(token):
    key = getTokenKey()
    return redisConn.set(key, token, ex=7200)
