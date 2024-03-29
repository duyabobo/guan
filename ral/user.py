#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pickle

from util.redis_conn import redisConn

finishCntKey = "UserModel:infoFinishCnt"


def getKey():
    return "wx:miniprogram:user:fill_finish:set"


def addFillFinishSet(passport_id):
    key = getKey()
    redisConn.sadd(key, passport_id)
    resetFinishCnt()


def delFillFinishSet(passport_id):
    key = getKey()
    redisConn.srem(key, passport_id)
    resetFinishCnt()


def resetFinishCnt():
    key = getKey()
    finishCnt = redisConn.scard(key)
    redisConn.set(finishCntKey, pickle.dumps(finishCnt), ex=3600)
