#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.redis_conn import redisConn


def getKey(dataName, passportId):
    return "dataName:{}:afterColumnChange:{}".format(dataName, passportId)


def setDataIdAfterColumnChange(dataName, passportId, educationId):
    """
    临时存储用户修改多重选择器的结果
    """
    key = getKey(dataName, passportId)
    return redisConn.set(key, educationId, ex=7200)


def getDataIdAfterColumnChange(dataName, passportId):
    """
    返回临时修改的多重选择结果
    """
    key = getKey(dataName, passportId)
    return redisConn.get(key)


def delDataIdAfterConfirm(dataName, passportId):
    """
    确认重新选择信息，删除临时选择结果
    """
    key = getKey(dataName, passportId)
    return redisConn.delete(key)
