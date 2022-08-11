#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.redis_conn import redisConn


def getKey():
    return "wx:miniprogram:user:fill_finish:set"


def getFillFinishCnt():
    key = getKey()
    return redisConn.scard(key) or 0


def addFillFinishSet(passport_id):
    key = getKey()
    return redisConn.sadd(key, passport_id)
