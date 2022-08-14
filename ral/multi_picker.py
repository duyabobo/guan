#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.redis_conn import redisConn


def getKey(opType, passportId):
    return "opType:{}:afterColumnChange:{}".format(opType, passportId)


def setDataIdAfterColumnChange(opType, passportId, educationId):
    """
    临时存储用户修改多重选择器的结果
    """
    key = getKey(opType, passportId)
    return redisConn.set(key, educationId, ex=7200)


def getDataIdAfterColumnChange(opType, passportId):
    """
    返回临时修改的多重选择结果
    """
    key = getKey(opType, passportId)
    return redisConn.get(key)


def delDataIdAfterConfirm(opType, passportId):
    """
    确认重新选择信息，删除临时选择结果
    """
    key = getKey(opType, passportId)
    return redisConn.delete(key)
