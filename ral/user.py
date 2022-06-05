#! /usr/bin/env python
# -*- coding: utf-8 -*-

def getKey():
    return "wx:miniprogram:user:fill_finish:set"


def getFillFinishCnt(redis):
    key = getKey()
    return redis.scard(key) or 0


def addFillFinishSet(redis, passport_id):
    key = getKey()
    return redis.sadd(key, passport_id)
