#! /usr/bin/env python
# -*- coding: utf-8 -*-
from service.common.selector import SingleSelector
from util.const.match import *


OP_FUNCS = [  # 真正生效的用户信息字段操作类型
    OP_TYPE_SEX,
    OP_TYPE_BIRTH_YEAR,
    OP_TYPE_HEIGHT,
    OP_TYPE_WEIGHT,
    OP_TYPE_MONTH_PAY,
    OP_TYPE_MARTIAL_STATUS,
    OP_TYPE_EDUCATION,
]


def SingleSelectorFactory(op_type, data):
    if op_type == OP_TYPE_SEX:
        return SingleSelector("性别", data.sex, data.sex, op_type)
    elif op_type == OP_TYPE_BIRTH_YEAR:
        return SingleSelector("出生年份", data.birth_year, "出生于%d年" % data.birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT:
        return SingleSelector("身高(cm)", data.height, "身高%scm" % data.height, op_type)
    elif op_type == OP_TYPE_WEIGHT:
        return SingleSelector("体重(kg)", data.weight, "体重%skg" % data.weight, op_type)
    elif op_type == OP_TYPE_MONTH_PAY:
        return SingleSelector("税前月收入(元)", data.month_pay, "月收入(税前)%s元" % data.month_pay, op_type)
    elif op_type == OP_TYPE_MARTIAL_STATUS:
        return SingleSelector("婚姻现状", data.martial_status, data.martial_status, op_type)
    elif op_type == OP_TYPE_EDUCATION:
        return SingleSelector("学历", data.education, data.education, op_type)


class UserHelper(object):

    def __init__(self, user):
        self.user = user

    def getInformationList(self):
        informationList = []
        for op_func in OP_FUNCS:
            info = SingleSelectorFactory(op_func, self.user)
            if info:
                informationList.append(info)
        return informationList

    @property
    def hasFillFinish(self):
        informationList = self.getInformationList()
        return reduce(lambda x, y: x and y, [i.hasFilled for i in informationList])

    def getUpdateParams(self, opType, valueIndex):
        updateParams = {}
        if opType == OP_TYPE_SEX and int(valueIndex) != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_BIRTH_YEAR:
            updateParams['birth_year'] = BIRTH_YEAR_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = MARTIAL_STATUS_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_HEIGHT:
            updateParams['height'] = HEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_WEIGHT:
            updateParams['weight'] = WEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_MONTH_PAY:
            updateParams['month_pay'] = MONTH_PAY_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_EDUCATION:
            updateParams['education'] = EDUCATION_CHOICE_LIST[int(valueIndex)]
        return updateParams
