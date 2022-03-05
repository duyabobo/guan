#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from util import const


class MatchHelper(object):  # todo 拆分成两个helper

    def __init__(self, info, isUserNotRequirement=True):
        self.info = info
        self.isUserNotRequirement = isUserNotRequirement

    @property
    def sexValue(self):
        return self.info.sex

    @property
    def sexIndex(self):
        try:
            return const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST.index(self.sexValue)
        except:
            return -1

    @property
    def birthYearValue(self):
        if self.isUserNotRequirement:
            return self.info.birth_year
        else:
            raise Exception("birth_year 无法获取")

    @property
    def birthYearIndex(self):
        try:
            return const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST.index(self.birthYearValue)
        except:
            return -1

    @property
    def educationMinValue(self):
        if not self.isUserNotRequirement:
            return self.info.min_education
        else:
            raise Exception("min_education 无法获取")

    @property
    def educationMaxValue(self):
        if not self.isUserNotRequirement:
            return self.info.max_education
        else:
            raise Exception("max_education 无法获取")

    @property
    def selectEducationMinIndex(self):
        if not self.isUserNotRequirement:
            defaultMin = self.educationMinValue
            try:
                return const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD_CHOICE_LIST.index(defaultMin)
            except:
                return 0
        else:
            raise Exception("min_education 无法获取")

    @property
    def selectEducationMaxIndex(self):
        if not self.isUserNotRequirement:
            defaultMax = self.educationMaxValue
            try:
                return const.MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST.index(defaultMax)
            except:
                return 0
        else:
            raise Exception("min_education 无法获取")

    @property
    def birthYearMinValue(self):
        if not self.isUserNotRequirement:
            return self.info.min_birth_year
        else:
            raise Exception("min_birth_year 无法获取")

    @property
    def selectBirthYearMinIndex(self):
        if not self.isUserNotRequirement:
            defaultMin = self.birthYearMinValue or const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST.index(defaultMin)
            except:
                return 0
        else:
            raise Exception("min_birth_year 无法获取")

    @property
    def birthYearMaxValue(self):
        if not self.isUserNotRequirement:
            return self.info.max_birth_year
        else:
            raise Exception("max_birth_year 无法获取")

    @property
    def selectBirthYearMaxIndex(self):
        if not self.isUserNotRequirement:
            defaultMax = self.birthYearMaxValue or const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST.index(defaultMax)
            except:
                return 0
        else:
            raise Exception("max_birth_year 无法获取")

    @property
    def weightMinValue(self):
        if not self.isUserNotRequirement:
            return self.info.min_weight
        else:
            raise Exception("min_weight 无法获取")

    @property
    def selectWeightMinIndex(self):
        if not self.isUserNotRequirement:
            minWeight = self.weightMinValue or const.GOOD_WEIGHT
            try:
                return const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST.index(minWeight)
            except:
                return 0
        else:
            raise Exception("min_weight 无法获取")

    @property
    def weightMaxValue(self):
        if not self.isUserNotRequirement:
            return self.info.max_weight
        else:
            raise Exception("max_weight 无法获取")

    @property
    def selectWeightMaxIndex(self):
        if not self.isUserNotRequirement:
            maxWeight = self.weightMaxValue or const.GOOD_WEIGHT
            try:
                return const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST.index(maxWeight)
            except:
                return 0
        else:
            raise Exception("max_weight 无法获取")

    @property
    def heightMinValue(self):
        if not self.isUserNotRequirement:
            return self.info.min_height
        else:
            raise Exception("min_height 无法获取")

    @property
    def selectHeightMinIndex(self):
        if not self.isUserNotRequirement:
            minHeight = self.heightMinValue or const.GOOD_HEIGHT
            try:
                return const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD_CHOICE_LIST.index(minHeight)
            except:
                return 0
        else:
            raise Exception("min_height 无法获取")

    @property
    def heightMaxValue(self):
        if not self.isUserNotRequirement:
            return self.info.max_height
        else:
            raise Exception("max_height 无法获取")

    @property
    def selectHeightMaxIndex(self):
        if not self.isUserNotRequirement:
            maxValue = self.heightMaxValue or const.GOOD_HEIGHT
            try:
                return const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD_CHOICE_LIST.index(maxValue)
            except:
                return 0
        else:
            raise Exception("max_height 无法获取")

    @property
    def monthPayMinValue(self):
        if not self.isUserNotRequirement:
            return self.info.min_month_pay
        else:
            raise Exception("min_month_pay 无法获取")

    @property
    def selectMonthPayMinIndex(self):
        if not self.isUserNotRequirement:
            minMonthPay = self.monthPayMinValue or const.GOOD_MONTH_PAY
            try:
                return const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD_CHOICE_LIST.index(minMonthPay)
            except:
                return 0
        else:
            raise Exception("min_month_pay 无法获取")

    @property
    def monthPayMaxValue(self):
        if not self.isUserNotRequirement:
            return self.info.max_month_pay
        else:
            raise Exception("min_month_pay 无法获取")

    @property
    def selectMonthPayMaxIndex(self):
        if not self.isUserNotRequirement:
            maxValue = self.monthPayMaxValue or const.GOOD_MONTH_PAY
            try:
                return const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD_CHOICE_LIST.index(maxValue)
            except:
                return 0
        else:
            raise Exception("min_month_pay 无法获取")

    @property
    def martialStatusValue(self):
        return self.info.martial_status

    @property
    def martialStatusIndex(self):
        try:
            return const.MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST.index(self.martialStatusValue)
        except:
            return -1

    @property
    def heightValue(self):
        return self.info.height

    @property
    def heightIndex(self):
        try:
            return const.MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST.index(self.heightValue)
        except:
            return -1

    @property
    def weightValue(self):
        return self.info.weight

    @property
    def weightIndex(self):
        try:
            return const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST.index(self.weightValue)
        except:
            return -1

    @property
    def monthPayValue(self):
        return self.info.month_pay

    @property
    def monthPayIndex(self):
        try:
            return const.MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST.index(self.monthPayValue)
        except:
            return -1

    @property
    def educationValue(self):
        return self.info.education

    @property
    def educationIndex(self):
        try:
            return const.MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST.index(self.educationValue)
        except:
            return -1

    def getSexInfo(self):
        return {
            "desc": "性别",
            "bindChange": "updateSex",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.sexValue,
            "selectValueIndex": self.sexIndex if self.sexIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_SEX_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST,
        }

    def getBirthYearInfo(self):
        return {
            "desc": "周5是否有时间",
            "bindChange": "updateBirthYear",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.birthYearValue or "",
            "selectValueIndex": self.birthYearIndex if self.birthYearIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST,
        }

    def getHeight(self):
        return {
            "desc": "周六是否有时间",
            "bindChange": "updateHeight",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.heightValue or "",
            "selectValueIndex": self.heightIndex if self.heightIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_HEIGHT_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST,
        }

    def getWeight(self):
        return {
            "desc": "周日是否有时间",
            "bindChange": "updateWeight",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.weightValue or "",
            "selectValueIndex": self.weightIndex if self.weightIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_WEIGHT_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST,
        }

    def getMonthPay(self):
        return {
            "desc": "税前月收入(元)",
            "bindChange": "updateMonthPay",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.monthPayValue or "",
            "selectValueIndex": self.monthPayIndex if self.monthPayIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_MONTH_PAY_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST,
        }

    def getMartialStatus(self):
        return {
            "desc": "婚姻现状",
            "bindChange": "updateMartialStatus",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.martialStatusValue,
            "selectValueIndex": self.martialStatusIndex if self.martialStatusIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_MARTIAL_STATUS_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST,
        }

    def getEducation(self):
        return {
            "desc": "学历",
            "bindChange": "updateEducation",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.educationValue,
            "selectValueIndex": self.educationIndex if self.educationIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_EDUCATION_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST,
        }

    def getMartialStatusPeriod(self):
        return {
            "desc": "婚姻",
            "bindChange": "updateMartialStatus",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.martialStatusValue,
            "selectValueIndex": self.martialStatusIndex if self.martialStatusIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_MARTIAL_STATUS_INDEX,
            "choiceList": const.MODEL_USER_OP_TYPE_MARTIAL_STATUS_PERIOD_CHOICE_LIST,
        }

    def getEducationPeriod(self):
        return {
            "desc": "学历区间",
            "bindChange": "updateEducationPeriod",
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,
            "bindColumnChange": "educationPeriodColumnChange",
            "fromValue": self.educationMinValue,
            "toValue": self.educationMaxValue,
            "fromAndToSelectValueIndex": [self.selectEducationMinIndex, self.selectEducationMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD_CHOICE_LIST, const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD_CHOICE_LIST],
        }

    def getBirthYearPeriod(self):
        return {
            "desc": "周五上午下午",
            "bindChange": "updateBirthYearPeriod",   
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "birthYearPeriodColumnChange",  
            "fromValue": self.birthYearMinValue,   
            "toValue": self.birthYearMaxValue,  
            "fromAndToSelectValueIndex": [self.selectBirthYearMinIndex, self.selectBirthYearMaxIndex],   
            "fromAndToChoiceList": [const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST, const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST],
        }

    def getWeightPeriod(self):
        return {
            "desc": "周日时间段",
            "bindChange": "updateWeightPeriod",   
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "weightPeriodColumnChange",  
            "fromValue": self.weightMinValue,
            "toValue": self.weightMaxValue,
            "fromAndToSelectValueIndex": [self.selectWeightMinIndex, self.selectWeightMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_OP_TYPE_WEIGHT_PERIOD_CHOICE_LIST, const.MODEL_USER_OP_TYPE_WEIGHT_PERIOD_CHOICE_LIST],
        }

    def getHeightPeriod(self):
        return {
            "desc": "周六时间段",
            "bindChange": "updateHeightPeriod",   
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,  
            "bindColumnChange": "heightPeriodColumnChange",  
            "fromValue": self.heightMinValue,
            "toValue": self.heightMaxValue,
            "fromAndToSelectValueIndex": [self.selectHeightMinIndex, self.selectHeightMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD_CHOICE_LIST, const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD_CHOICE_LIST],
        }

    def getMonthPayPeriod(self):
        return {
            "desc": "税前月收入区间(元)",
            "bindChange": "updateMonthPayPeriod",
            "pickerType": const.PICKER_TYPE_MULTI_SELECTOR,
            "bindColumnChange": "monthPayPeriodColumnChange",
            "fromValue": self.monthPayMinValue,
            "toValue": self.monthPayMaxValue,
            "fromAndToSelectValueIndex": [self.selectMonthPayMinIndex, self.selectMonthPayMaxIndex],
            "fromAndToChoiceList": [const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD_CHOICE_LIST, const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD_CHOICE_LIST],
        }

    def getUpdateParams(self, opType, valueIndex):
        updateParams = {}
        if opType == const.MODEL_USER_OP_TYPE_SEX and int(valueIndex) != const.MODEL_SEX_UNKNOWN:
            updateParams['sex'] = const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_BIRTH_YEAR:
            updateParams['birth_year'] = const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = const.MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_HEIGHT:
            updateParams['height'] = const.MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_WEIGHT:
            updateParams['weight'] = const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_MONTH_PAY:
            updateParams['month_pay'] = const.MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_EDUCATION:
            updateParams['education'] = const.MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_birth_year'] = const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST[value[0]]
            updateParams['max_birth_year'] = const.MODEL_USER_OP_TYPE_BIRTH_YEAR_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_WEIGHT_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_weight'] = const.MODEL_USER_OP_TYPE_WEIGHT_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_weight'] = const.MODEL_USER_OP_TYPE_WEIGHT_PERIOD_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_height'] = const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_height'] = const.MODEL_USER_OP_TYPE_HEIGHT_PERIOD_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_month_pay'] = const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_month_pay'] = const.MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD_CHOICE_LIST[value[1]]
        elif opType == const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD:
            value = json.loads(valueIndex)
            updateParams['min_education'] = const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD_CHOICE_LIST[value[0]]
            updateParams['max_education'] = const.MODEL_USER_OP_TYPE_EDUCATION_PERIOD_CHOICE_LIST[value[1]]
        return updateParams
