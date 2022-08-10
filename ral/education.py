#! /usr/bin/env python
# -*- coding: utf-8 -*-

def getKey(passportId):
    return "education:educationId:afterColumnChange:{}".format(passportId)


def setEducationIdAfterColumnChange(redis, passportId, educationId):
    """
    临时存储用户修改教育多重选择器的结果
    """
    key = getKey(passportId)
    return redis.set(key, educationId, ex=7200)


def getEducationIdAfterColumnChange(redis, passportId):
    """
    返回临时修改的教育多重选择结果
    """
    key = getKey(passportId)
    return redis.get(key)


def delEducationIdAfterConfirm(redis, passportId):
    """
    确认重新选择教育信息，删除临时选择结果
    """
    key = getKey(passportId)
    return redis.delete(key)
