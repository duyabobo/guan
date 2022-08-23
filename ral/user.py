#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.redis_conn import redisConn

finishCntKey = "UserModel:infoFinishCnt"


def getKey():
    return "wx:miniprogram:user:fill_finish:set"


def addFillFinishSet(passport_id):
    redisConn.incr(finishCntKey)
    redisConn.expire(finishCntKey, 3600)
    key = getKey()
    return redisConn.sadd(key, passport_id)


def delFillFinishSet(passport_id):
    redisConn.decr(finishCntKey)
    redisConn.expire(finishCntKey, 3600)
    key = getKey()
    return redisConn.srem(key, passport_id)
