#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.education import EducationModel
from model.work import WorkModel
from util.const.match import OP_TYPE_EDUCATION_MULTI, OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE, \
    OP_TYPE_WORK_MULTI_COLUMN_CHANGE, OP_TYPE_WORK_MULTI
from util.redis_conn import redisConn


education_config = {
    "model": EducationModel,
    "dataName": "education",
    "firstName": "category",
    "secondName": "disciplines",
    "thirdName": "major"
}

work_config = {
    "model": WorkModel,
    "dataName": "work",
    "firstName": "profession",
    "secondName": "industry",
    "thirdName": "position"
}

multi_picker_config = {
    OP_TYPE_EDUCATION_MULTI: education_config,
    OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE: education_config,
    OP_TYPE_WORK_MULTI_COLUMN_CHANGE: work_config,
    OP_TYPE_WORK_MULTI: work_config,
}


def getCacheKeyPrefix(opType):
    return multi_picker_config[opType]['dataName']


def getKey(opType, passportId):
    cacheKeyPrefix = getCacheKeyPrefix(opType)
    return "dataName:{}:afterColumnChange:{}".format(cacheKeyPrefix, passportId)


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
