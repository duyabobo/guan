#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from util.const.match import *
from service.common.selector import SingleSelector, MultiSelector


OP_FUNCS = [  # 真正生效的期望条件字段变更方法名列表
    OP_TYPE_SEX,
    OP_BIRTH_YEAR_PERIOD,
    OP_TYPE_HEIGHT_PERIOD,
    OP_TYPE_WEIGHT_PERIOD,
    OP_TYPE_MONTH_PAY_PERIOD,
    OP_TYPE_EDUCATION_PERIOD,
    OP_TYPE_MARTIAL_STATUS,
]


def selectorFactory(op_type, data):
    if op_type == OP_TYPE_SEX:
        return SingleSelector("性别", data.sex, data.sex, op_type)
    elif op_type == OP_TYPE_MARTIAL_STATUS:
        return SingleSelector("婚姻现状", data.martial_status, data.martial_status, op_type)
    elif op_type == OP_BIRTH_YEAR_PERIOD:
        return MultiSelector("出生年份区间", data.min_birth_year, data.max_birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT_PERIOD:
        return MultiSelector("身高区间(cm)", data.min_height, data.max_height, op_type)
    elif op_type == OP_TYPE_WEIGHT_PERIOD:
        return MultiSelector("体重区间(kg)", data.min_weight, data.max_weight, op_type)
    elif op_type == OP_TYPE_MONTH_PAY_PERIOD:
        return MultiSelector("税前月收入区间(元)", data.min_month_pay, data.max_month_pay, op_type)
    elif op_type == OP_TYPE_EDUCATION_PERIOD:
        return MultiSelector("学历区间", data.min_education, data.max_education, op_type)


class RequirementHelper(object):

    def __init__(self, requirement):
        self.requirement = requirement
        
    def getRequirementList(self):
        requirementList = []
        for op_func in OP_FUNCS:
            requirement = selectorFactory(op_func, self.requirement)
            if requirement:
                requirementList.append(requirement)
        return requirementList

    def getUpdateParams(self, opType, valueIndex):
        updateParams = {}
        if opType == OP_TYPE_SEX and int(valueIndex) != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_BIRTH_YEAR_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_birth_year'] = BIRTH_YEAR_CHOICE_LIST[value[0]]
            updateParams['max_birth_year'] = BIRTH_YEAR_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = MARTIAL_STATUS_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_WEIGHT_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_weight'] = WEIGHT_CHOICE_LIST[value[0]]
            updateParams['max_weight'] = WEIGHT_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_HEIGHT_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_height'] = HEIGHT_CHOICE_LIST[value[0]]
            updateParams['max_height'] = HEIGHT_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_MONTH_PAY_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_month_pay'] = MONTH_PAY_CHOICE_LIST[value[0]]
            updateParams['max_month_pay'] = MONTH_PAY_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_EDUCATION_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_education'] = EDUCATION_CHOICE_LIST[value[0]]
            updateParams['max_education'] = EDUCATION_CHOICE_LIST[value[1]]
        return updateParams
