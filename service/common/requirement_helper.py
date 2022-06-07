#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from util import const

REQUIREMENT_GET_FUNCS = [  # 真正生效的期望条件字段获取方法
    'getSexInfo',
    'getBirthYearPeriod',
    'getHeightPeriod',
    'getWeightPeriod',
    'getEducationPeriod',
    'getMonthPayPeriod',
    'getMartialStatusPeriod',
]


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
        if opType == const.MODEL_USER_OP_TYPE_SEX and int(valueIndex) != const.MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = const.MODEL_USER_SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_birth_year'] = const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST[value[0]]
            updateParams['max_birth_year'] = const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = const.MODEL_USER_MARTIAL_STATUS_PERIOD_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_WEIGHT_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_weight'] = const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_weight'] = const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_height'] = const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_height'] = const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_month_pay'] = const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_month_pay'] = const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_education'] = const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_education'] = const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST[value[1]]
        return updateParams

    def getSexInfo(self):
        def _sexIndex():
            try:
                return const.MODEL_USER_SEX_CHOICE_LIST.index(
                    self.requirement.sex) or const.MODEL_USER_DEFAULT_SEX_INDEX
            except:
                return const.MODEL_USER_DEFAULT_SEX_INDEX

        return {
            "desc": "性别",
            "bindChange": const.MODEL_USER_OP_TYPE_SEX,
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.requirement.sex,
            "selectValueIndex": _sexIndex(),
            "choiceList": const.MODEL_USER_SEX_CHOICE_LIST,
        }

    def getMartialStatusPeriod(self):
        def _martialStatusIndex():
            try:
                return const.MODEL_USER_MARTIAL_STATUS_CHOICE_LIST.index(
                    self.requirement.martial_status) or const.MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX
            except:
                return const.MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX

        return {
            "desc": "婚姻",
            "bindChange": const.MODEL_USER_OP_TYPE_MARTIAL_STATUS,
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.requirement.martial_status,
            "selectValueIndex": _martialStatusIndex(),
            "choiceList": const.MODEL_USER_MARTIAL_STATUS_PERIOD_CHOICE_LIST,
        }

    def getEducationPeriod(self):
        def _selectEducationMinIndex():
            defaultMin = self.requirement.min_education
            try:
                return const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST.index(defaultMin)
            except:
                return 0

        def _selectEducationMaxIndex():
            defaultMax = self.requirement.max_education
            try:
                return const.MODEL_USER_EDUCATION_CHOICE_LIST.index(defaultMax)
            except:
                return 0

        return {
            "desc": "学历区间",
            "bindChange": const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD,
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,
            "bindColumnChange": "educationPeriodColumnChange",
            "fromValue": self.requirement.min_education,
            "toValue": self.requirement.max_education,
            "fromAndToSelectValueIndex": [_selectEducationMinIndex(), _selectEducationMaxIndex()],
            "fromAndToChoiceList": [const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST, const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST],
        }

    def getBirthYearPeriod(self):
        def _selectBirthYearMinIndex():
            defaultMin = self.requirement.min_birth_year or const.MODEL_USER_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(defaultMin)
            except:
                return 0

        def _selectBirthYearMaxIndex():
            defaultMax = self.requirement.max_birth_year or const.MODEL_USER_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(defaultMax)
            except:
                return 0

        return {
            "desc": "出生年份区间",   
            "bindChange": const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD,
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "birthYearPeriodColumnChange",  
            "fromValue": self.requirement.min_birth_year,
            "toValue": self.requirement.max_birth_year,
            "fromAndToSelectValueIndex": [_selectBirthYearMinIndex(), _selectBirthYearMaxIndex()],
            "fromAndToChoiceList": [const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST, const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST],
        }

    def getWeightPeriod(self):
        def _selectWeightMinIndex():
            minWeight = self.requirement.min_weight or const.GOOD_WEIGHT
            try:
                return const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST.index(minWeight)
            except:
                return 0

        def _selectWeightMaxIndex():
            maxWeight = self.requirement.max_weight or const.GOOD_WEIGHT
            try:
                return const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST.index(maxWeight)
            except:
                return 0

        return {
            "desc": "体重区间(kg)",
            "bindChange": const.MODEL_USER_OP_TYPE_WEIGHT_PERIOD,
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "weightPeriodColumnChange",  
            "fromValue": self.requirement.min_weight,
            "toValue": self.requirement.max_weight,
            "fromAndToSelectValueIndex": [_selectWeightMinIndex(), _selectWeightMaxIndex()],
            "fromAndToChoiceList": [const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST, const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST],
        }

    def getHeightPeriod(self):
        def _selectHeightMinIndex():
            minHeight = self.requirement.min_height or const.GOOD_HEIGHT
            try:
                return const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST.index(minHeight)
            except:
                return 0

        def _selectHeightMaxIndex():
            maxValue = self.requirement.max_height or const.GOOD_HEIGHT
            try:
                return const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST.index(maxValue)
            except:
                return 0

        return {
            "desc": "身高区间(cm)",
            "bindChange": const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD,
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "heightPeriodColumnChange",  
            "fromValue": self.requirement.min_height,
            "toValue": self.requirement.max_height,
            "fromAndToSelectValueIndex": [_selectHeightMinIndex(), _selectHeightMaxIndex()],
            "fromAndToChoiceList": [const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST, const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST],
        }

    def getMonthPayPeriod(self):
        def _selectMonthPayMinIndex():
            minMonthPay = self.requirement.min_month_pay or const.GOOD_MONTH_PAY
            try:
                return const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST.index(minMonthPay)
            except:
                return 0

        def _selectMonthPayMaxIndex():
            maxValue = self.requirement.max_month_pay or const.GOOD_MONTH_PAY
            try:
                return const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST.index(maxValue)
            except:
                return 0

        return {
            "desc": "税前月收入区间(元)",
            "bindChange": const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD,
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,
            "bindColumnChange": "monthPayPeriodColumnChange",
            "fromValue": self.requirement.min_month_pay,
            "toValue": self.requirement.max_month_pay,
            "fromAndToSelectValueIndex": [_selectMonthPayMinIndex(), _selectMonthPayMaxIndex()],
            "fromAndToChoiceList": [const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST, const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST],
        }
