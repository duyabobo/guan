#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from util import const

USER_INFO_GET_SEX = 'getSexInfo'
USER_INFO_GET_MARTIAL_STATUS_PERIOD = 'getMartialStatusPeriod'
USER_INFO_GET_EDUCATION_PERIOD = 'getEducationPeriod'
USER_INFO_GET_BIRTH_YEAR_PERIOD = 'getBirthYearPeriod'
USER_INFO_GET_WEIGHT_PERIOD = 'getWeightPeriod'
USER_INFO_GET_HEIGHT_PERIOD = 'getHeightPeriod'
USER_INFO_GET_MONTH_PAY_PERIOD = 'getMonthPayPeriod'

REQUIREMENT_GET_FUNCS = [
    USER_INFO_GET_SEX,
    USER_INFO_GET_BIRTH_YEAR_PERIOD,
    USER_INFO_GET_HEIGHT_PERIOD,
    USER_INFO_GET_WEIGHT_PERIOD,
    USER_INFO_GET_EDUCATION_PERIOD,
    USER_INFO_GET_MONTH_PAY_PERIOD,
    USER_INFO_GET_MARTIAL_STATUS_PERIOD,
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

    @property
    def sexIndex(self):
        try:
            return const.MODEL_USER_SEX_CHOICE_LIST.index(self.requirement.sex) or const.MODEL_USER_DEFAULT_SEX_INDEX
        except:
            return const.MODEL_USER_DEFAULT_SEX_INDEX

    @property
    def selectEducationMinIndex(self):
        defaultMin = self.requirement.min_education
        try:
            return const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST.index(defaultMin)
        except:
            return 0

    @property
    def selectEducationMaxIndex(self):
        defaultMax = self.requirement.max_education
        try:
            return const.MODEL_USER_EDUCATION_CHOICE_LIST.index(defaultMax)
        except:
            return 0

    @property
    def selectBirthYearMinIndex(self):
        defaultMin = self.requirement.min_birth_year or const.MODEL_USER_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
        try:
            return const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(defaultMin)
        except:
            return 0

    @property
    def selectBirthYearMaxIndex(self):
        defaultMax = self.requirement.max_birth_year or const.MODEL_USER_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
        try:
            return const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(defaultMax)
        except:
            return 0

    @property
    def selectWeightMinIndex(self):
        minWeight = self.requirement.min_weight or const.GOOD_WEIGHT
        try:
            return const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST.index(minWeight)
        except:
            return 0

    @property
    def selectWeightMaxIndex(self):
        maxWeight = self.requirement.max_weight or const.GOOD_WEIGHT
        try:
            return const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST.index(maxWeight)
        except:
            return 0

    @property
    def selectHeightMinIndex(self):
        minHeight = self.requirement.min_height or const.GOOD_HEIGHT
        try:
            return const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST.index(minHeight)
        except:
            return 0

    @property
    def selectHeightMaxIndex(self):
        maxValue = self.requirement.max_height or const.GOOD_HEIGHT
        try:
            return const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST.index(maxValue)
        except:
            return 0

    @property
    def selectMonthPayMinIndex(self):
        minMonthPay = self.requirement.min_month_pay or const.GOOD_MONTH_PAY
        try:
            return const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST.index(minMonthPay)
        except:
            return 0

    @property
    def selectMonthPayMaxIndex(self):
        maxValue = self.requirement.max_month_pay or const.GOOD_MONTH_PAY
        try:
            return const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST.index(maxValue)
        except:
            return 0

    @property
    def martialStatusIndex(self):
        try:
            return const.MODEL_USER_MARTIAL_STATUS_CHOICE_LIST.index(self.requirement.martial_status) or const.MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX
        except:
            return const.MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX

    def getSexInfo(self):
        return {
            "desc": "性别",
            "bindChange": "updateSex",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.requirement.sex,
            "selectValueIndex": self.sexIndex,
            "choiceList": const.MODEL_USER_SEX_CHOICE_LIST,
        }

    def getMartialStatusPeriod(self):
        return {
            "desc": "婚姻",
            "bindChange": "updateMartialStatus",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.requirement.martial_status,
            "selectValueIndex": self.martialStatusIndex,
            "choiceList": const.MODEL_USER_MARTIAL_STATUS_PERIOD_CHOICE_LIST,
        }

    def getEducationPeriod(self):
        return {
            "desc": "学历区间",
            "bindChange": "updateEducationPeriod",
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,
            "bindColumnChange": "educationPeriodColumnChange",
            "fromValue": self.requirement.min_education,
            "toValue": self.requirement.max_education,
            "fromAndToSelectValueIndex": [self.selectEducationMinIndex, self.selectEducationMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST, const.MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST],
        }

    def getBirthYearPeriod(self):
        return {
            "desc": "出生年份区间",   
            "bindChange": "updateBirthYearPeriod",   
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "birthYearPeriodColumnChange",  
            "fromValue": self.requirement.min_birth_year,
            "toValue": self.requirement.max_birth_year,
            "fromAndToSelectValueIndex": [self.selectBirthYearMinIndex, self.selectBirthYearMaxIndex],   
            "fromAndToChoiceList": [const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST, const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST],
        }

    def getWeightPeriod(self):
        return {
            "desc": "体重区间(kg)",
            "bindChange": "updateWeightPeriod",   
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "weightPeriodColumnChange",  
            "fromValue": self.requirement.min_weight,
            "toValue": self.requirement.max_weight,
            "fromAndToSelectValueIndex": [self.selectWeightMinIndex, self.selectWeightMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST, const.MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST],
        }

    def getHeightPeriod(self):
        return {
            "desc": "身高区间(cm)",
            "bindChange": "updateHeightPeriod",   
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "heightPeriodColumnChange",  
            "fromValue": self.requirement.min_height,
            "toValue": self.requirement.max_height,
            "fromAndToSelectValueIndex": [self.selectHeightMinIndex, self.selectHeightMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST, const.MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST],
        }

    def getMonthPayPeriod(self):
        return {
            "desc": "税前月收入区间(元)",
            "bindChange": "updateMonthPayPeriod",
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,
            "bindColumnChange": "monthPayPeriodColumnChange",
            "fromValue": self.requirement.min_month_pay,
            "toValue": self.requirement.max_month_pay,
            "fromAndToSelectValueIndex": [self.selectMonthPayMinIndex, self.selectMonthPayMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST, const.MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST],
        }

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
