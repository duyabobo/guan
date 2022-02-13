#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from util import const


class MatchHelper(object):

    def __init__(self, info, isUserNotRequirement=True):
        self.info = info
        self.isUserNotRequirement = isUserNotRequirement

    @property
    def sexValue(self):
        return const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST[self.info.sex]

    @property
    def birthYearValue(self):
        if self.isUserNotRequirement:
            return self.info.birth_year
        else:
            raise Exception("birth_year 无法获取")

    @property
    def defaultBirthYear(self):
        if self.isUserNotRequirement:
            return self.birthYearValue or const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR
        else:
            raise Exception("birth_year 无法获取")

    @property
    def birthMinYearValue(self):
        if not self.isUserNotRequirement:
            return self.info.min_birth_year
        else:
            raise Exception("min_birth_year 无法获取")

    @property
    def defaultMinBirthYearIndex(self):
        if not self.isUserNotRequirement:
            defaultMin = self.birthMinYearValue or const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD_ARRAY.index(defaultMin)
            except:
                return 0
        else:
            raise Exception("min_birth_year 无法获取")

    @property
    def birthMaxYearValue(self):
        if not self.isUserNotRequirement:
            return self.info.max_birth_year
        else:
            raise Exception("max_birth_year 无法获取")

    @property
    def defaultMaxBirthYearIndex(self):
        if not self.isUserNotRequirement:
            defaultMax = self.birthMaxYearValue or const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR  # todo 可以和用户实际出生日期联通
            try:
                return const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD_ARRAY.index(defaultMax)
            except:
                return 0
        else:
            raise Exception("max_birth_year 无法获取")

    @property
    def martialStatus(self):
        return const.MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST[self.info.martial_status]

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
    def education(self):
        return const.MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST[self.info.education]

    def getSexInfo(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_SEX,
            "desc": "性别",
            "value": self.sexValue,
            "choiceList": const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST,
        }

    def getBirthYearInfo(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_BIRTH_YEAR,
            "desc": "出生年份",
            "value": self.birthYearValue or "",
            "start": "%s-01-01" % const.MODEL_USER_OP_TYPE_BIRTH_YEAR_START,
            "end": "%s-01-01" % const.MODEL_USER_OP_TYPE_BIRTH_YEAR_END,
            "defaultValue": self.defaultBirthYear,
        }

    def getRequirementBirthYearInfo(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD,
            "desc": "出生年份区间",
            "fromValue": self.birthMinYearValue,
            "toValue": self.birthMaxYearValue,
            "fromAndToArray": [const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD_ARRAY, const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD_ARRAY],
            "fromAndToIndex": [self.defaultMinBirthYearIndex, self.defaultMaxBirthYearIndex],
        }

    def getWeight(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_WEIGHT,
            "desc": "体重(kg)",
            "value": self.weightValue or "",
            "defaultValue": self.weightIndex if self.weightIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_WEIGHT,
            "choiceList": const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST,
        }

    def getHeight(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_HEIGHT,
            "desc": "身高(cm)",
            "value": self.heightValue or "",
            "defaultValue": self.heightIndex if self.heightIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_HEIGHT,
            "choiceList": const.MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST,
        }

    def getMonthPay(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_MONTH_PAY,
            "desc": "税前月收入(元)",
            "value": self.monthPayValue or "",
            "defaultValue": self.monthPayIndex if self.monthPayIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_MONTH_PAY,
            "choiceList": const.MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST,
        }

    def getOtherInfoList(self):
        return [
            {
                "opType": const.MODEL_USER_OP_TYPE_MARTIAL_STATUS,
                "desc": "婚姻现状",
                "value": self.martialStatus,
                "choiceList": const.MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST,
            },{
                "opType": const.MODEL_USER_OP_TYPE_EDUCATION,
                "desc": "学历",
                "value": self.education,
                "choiceList": const.MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST,
            },
        ]

    def getUpdateParams(self, opType, value):
        updateParams = {}
        if opType == const.MODEL_USER_OP_TYPE_SEX:
            updateParams['sex'] = value
        elif opType == const.MODEL_USER_OP_TYPE_BIRTH_YEAR:
            updateParams['birth_year'] = value
        elif opType == const.MODEL_USER_OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = value
        elif opType == const.MODEL_USER_OP_TYPE_HEIGHT:
            updateParams['height'] = const.MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST[int(value)]
        elif opType == const.MODEL_USER_OP_TYPE_WEIGHT:
            updateParams['weight'] = const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST[int(value)]
        elif opType == const.MODEL_USER_OP_TYPE_MONTH_PAY:
            updateParams['month_pay'] = const.MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST[int(value)]
        elif opType == const.MODEL_USER_OP_TYPE_EDUCATION:
            updateParams['education'] = value
        elif opType == const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD:
            value = json.loads(value)
            updateParams['min_birth_year'] = const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD_ARRAY[value[0]]
            updateParams['max_birth_year'] = const.MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD_ARRAY[value[1]]
        return updateParams
