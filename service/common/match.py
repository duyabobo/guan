#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util import const


class MatchHelper(object):

    def __init__(self, info, currentUserInfo=None):
        self.info = info
        self.currentUserInfo = currentUserInfo

    @property
    def sexValue(self):
        return const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST[self.info.sex]

    @property
    def birthYearValue(self):
        return self.info.birth_year

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
    def defaultBirthYear(self):
        return self.birthYearValue or const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR

    def getCurrentUserBirthYear(self):
        return int(self.currentUserInfo.birth_year)

    @property
    def defaultBirthYearPeriod(self):
        birthYear = self.getCurrentUserBirthYear()
        return "%s-%s年" % (birthYear - const.AGE_PERIOD, birthYear + const.AGE_PERIOD)

    @property
    def birthYearPeriodChoiceList(self):
        periodList = [
            "%s-%s年" % (max(const.MODEL_USER_OP_TYPE_BIRTH_YEAR_START, s - const.AGE_PERIOD), s)
            for s in range(self.getCurrentUserBirthYear(), const.MODEL_USER_OP_TYPE_BIRTH_YEAR_START, -const.AGE_PERIOD)
        ][::-1]
        periodList.extend(
            [
                "%s-%s年" % (s, min(const.MODEL_USER_OP_TYPE_BIRTH_YEAR_END, s + const.AGE_PERIOD))
                for s in range(self.getCurrentUserBirthYear(), const.MODEL_USER_OP_TYPE_BIRTH_YEAR_END, const.AGE_PERIOD)
            ]
        )
        return periodList

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

    def getbirthYearInfo(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_BIRTH_YEAR,
            "desc": "出生年份",
            "value": self.birthYearValue or "",
            "start": "%s-01-01" % const.MODEL_USER_OP_TYPE_BIRTH_YEAR_START,
            "end": "%s-01-01" % const.MODEL_USER_OP_TYPE_BIRTH_YEAR_END,
            "defaultValue": self.defaultBirthYear,
        }

    def getbirthYearPeriodInfo(self):
        # 获取出生年份区间列表
        return {
            "opType": const.MODEL_USER_OP_TYPE_BIRTH_YEAR,
            "desc": "出生年份",
            "value": self.weightValue,
            "defaultValue": self.defaultBirthYearPeriod,
            "choiceList": self.birthYearPeriodChoiceList,
        }

    def getWeight(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_WEIGHT,
            "desc": "体重",
            "value": self.weightValue or "",
            "defaultValue": self.weightIndex if self.weightIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_WEIGHT,
            "choiceList": const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST,
        }

    def getHeight(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_HEIGHT,
            "desc": "身高",
            "value": self.heightValue or "",
            "defaultValue": self.heightIndex if self.heightIndex > 0 else const.MODEL_USER_OP_TYPE_DEFAULT_HEIGHT,
            "choiceList": const.MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST,
        }

    def getMonthPay(self):
        return {
            "opType": const.MODEL_USER_OP_TYPE_MONTH_PAY,
            "desc": "月收入(税前)",
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
        return updateParams
