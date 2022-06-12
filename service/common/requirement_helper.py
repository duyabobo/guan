#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR
from util.const.match import *

REQUIREMENT_GET_FUNCS = [  # 真正生效的期望条件字段获取方法
    'getSexInfo',
    'getBirthYearPeriod',
    'getHeightPeriod',
    'getWeightPeriod',
    'getEducationPeriod',
    'getMonthPayPeriod',
    'getMartialStatusPeriod',
]


class RequirementSingleSelector(object):
    """择偶条件选择项数据结构：单项选择器"""
    def __init__(self, desc, bindChange, choiceList, value, selectValueIndex):
        self.desc = desc  # 条件名描述
        self.bindChange = bindChange  # 对应小程序的绑定方法
        self.pickerType = PICKER_TYPE_SELECTOR  # 选择器类型：单项
        self.choiceList = choiceList  # 条件可选范围列表
        self.value = value  # 条件当前值
        self.selectValueIndex = selectValueIndex  # 条件值对应的取值范围索引
        self.bindColumnChange = ''


class RequirementMultiSelector(object):
    def __init__(self, desc, bindChange, bindColumnChange, fromValue, toValue, fromAndToSelectValueIndex, fromAndToChoiceList):
        self.desc = desc
        self.pickerType = PICKER_TYPE_MULTI_SELECTOR  # 选择器类型：多项
        self.bindChange = bindChange
        self.bindColumnChange = bindColumnChange
        self.fromValue = fromValue
        self.toValue = toValue
        self.fromAndToSelectValueIndex = fromAndToSelectValueIndex
        self.fromAndToChoiceList = fromAndToChoiceList


class RequirementHelper(object):

    def __init__(self, requirement):
        self.requirement = requirement
        
    def getRequirementList(self):
        requirementList = []
        for func_name in REQUIREMENT_GET_FUNCS:
            func = self.__getattribute__(func_name)
            requirementList.append(func())
        return requirementList

    def getUpdateParams(self, opType, valueIndex):
        updateParams = {}
        if opType == OP_TYPE_SEX and int(valueIndex) != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == BIRTH_YEAR_PERIOD:
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

    def getSexInfo(self):
        def _sexIndex():
            try:
                return SEX_CHOICE_LIST.index(
                    self.requirement.sex) or DEFAULT_SEX_INDEX
            except:
                return DEFAULT_SEX_INDEX

        return RequirementSingleSelector("性别", OP_TYPE_SEX, SEX_CHOICE_LIST,
                                         self.requirement.sex, _sexIndex())

    def getMartialStatusPeriod(self):
        def _martialStatusIndex():
            try:
                return MARTIAL_STATUS_CHOICE_LIST.index(
                    self.requirement.martial_status) or DEFAULT_MARTIAL_STATUS_INDEX
            except:
                return DEFAULT_MARTIAL_STATUS_INDEX

        return RequirementSingleSelector("婚姻", OP_TYPE_MARTIAL_STATUS, MARTIAL_STATUS_CHOICE_LIST,
                                         self.requirement.martial_status, _martialStatusIndex())

    def getEducationPeriod(self):
        def _selectEducationMinIndex():
            defaultMin = self.requirement.min_education
            try:
                return EDUCATION_CHOICE_LIST.index(defaultMin)
            except:
                return 0

        def _selectEducationMaxIndex():
            defaultMax = self.requirement.max_education
            try:
                return EDUCATION_CHOICE_LIST.index(defaultMax)
            except:
                return 0

        return RequirementMultiSelector("学历区间", OP_TYPE_EDUCATION_PERIOD, "educationPeriodColumnChange",
                                        self.requirement.min_education, self.requirement.max_education,
                                        [_selectEducationMinIndex(), _selectEducationMaxIndex()],
                                        [EDUCATION_CHOICE_LIST, EDUCATION_CHOICE_LIST])

    def getBirthYearPeriod(self):
        def _selectBirthYearMinIndex():
            defaultMin = self.requirement.min_birth_year or DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return BIRTH_YEAR_CHOICE_LIST.index(defaultMin)
            except:
                return 0

        def _selectBirthYearMaxIndex():
            defaultMax = self.requirement.max_birth_year or DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return BIRTH_YEAR_CHOICE_LIST.index(defaultMax)
            except:
                return 0

        return RequirementMultiSelector("出生年份区间", BIRTH_YEAR_PERIOD, "birthYearPeriodColumnChange",
                                        self.requirement.min_birth_year, self.requirement.max_birth_year,
                                        [_selectBirthYearMinIndex(), _selectBirthYearMaxIndex()],
                                        [BIRTH_YEAR_CHOICE_LIST, BIRTH_YEAR_CHOICE_LIST])

    def getWeightPeriod(self):
        def _selectWeightMinIndex():
            minWeight = self.requirement.min_weight or GOOD_WEIGHT
            try:
                return WEIGHT_CHOICE_LIST.index(minWeight)
            except:
                return 0

        def _selectWeightMaxIndex():
            maxWeight = self.requirement.max_weight or GOOD_WEIGHT
            try:
                return WEIGHT_CHOICE_LIST.index(maxWeight)
            except:
                return 0

        return RequirementMultiSelector("体重区间(kg)", OP_TYPE_WEIGHT_PERIOD, "weightPeriodColumnChange",
                                        self.requirement.min_weight, self.requirement.max_weight,
                                        [_selectWeightMinIndex(), _selectWeightMaxIndex()],
                                        [WEIGHT_CHOICE_LIST, WEIGHT_CHOICE_LIST])

    def getHeightPeriod(self):
        def _selectHeightMinIndex():
            minHeight = self.requirement.min_height or GOOD_HEIGHT
            try:
                return HEIGHT_CHOICE_LIST.index(minHeight)
            except:
                return 0

        def _selectHeightMaxIndex():
            maxValue = self.requirement.max_height or GOOD_HEIGHT
            try:
                return HEIGHT_CHOICE_LIST.index(maxValue)
            except:
                return 0

        return RequirementMultiSelector("身高区间(cm)", OP_TYPE_HEIGHT_PERIOD, "heightPeriodColumnChange",
                                        self.requirement.min_height, self.requirement.max_height,
                                        [_selectHeightMinIndex(), _selectHeightMaxIndex()],
                                        [HEIGHT_CHOICE_LIST, HEIGHT_CHOICE_LIST])

    def getMonthPayPeriod(self):
        def _selectMonthPayMinIndex():
            minMonthPay = self.requirement.min_month_pay or GOOD_MONTH_PAY
            try:
                return MONTH_PAY_CHOICE_LIST.index(minMonthPay)
            except:
                return 0

        def _selectMonthPayMaxIndex():
            maxValue = self.requirement.max_month_pay or GOOD_MONTH_PAY
            try:
                return MONTH_PAY_CHOICE_LIST.index(maxValue)
            except:
                return 0

        return RequirementMultiSelector("税前月收入区间(元)", OP_TYPE_MONTH_PAY_PERIOD, "monthPayPeriodColumnChange",
                                        self.requirement.min_month_pay, self.requirement.max_month_pay,
                                        [_selectMonthPayMinIndex(), _selectMonthPayMaxIndex()],
                                        [MONTH_PAY_CHOICE_LIST, MONTH_PAY_CHOICE_LIST])
