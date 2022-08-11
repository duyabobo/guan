#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.redis_conn import redisConn


def getKey(passportId):
    return "education:educationId:afterColumnChange:{}".format(passportId)


def setEducationIdAfterColumnChange(passportId, educationId):
    """
    临时存储用户修改教育多重选择器的结果
    """
    key = getKey(passportId)
    return redisConn.set(key, educationId, ex=7200)


def getEducationIdAfterColumnChange(passportId):
    """
    返回临时修改的教育多重选择结果
    """
    key = getKey(passportId)
    return redisConn.get(key)


def delEducationIdAfterConfirm(passportId):
    """
    确认重新选择教育信息，删除临时选择结果
    """
    key = getKey(passportId)
    return redisConn.delete(key)
