#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util import const


class matchHelper(object):

    def __init__(self, info):
        self.info = info

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
    def height(self):
        return self.info.height

    @property
    def weight(self):
        return self.info.weight

    @property
    def monthPay(self):
        return self.info.month_pay

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
            "value": self.birthYearValue,
            "defaultValue": const.MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR,
        }

    def getOtherInfoList(self):
        return [
            {
                "opType": const.MODEL_USER_OP_TYPE_MARTIAL_STATUS,
                "desc": "婚姻现状",
                "value": self.martialStatus,
                "choiceList": const.MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST,
            },{
                "opType": const.MODEL_USER_OP_TYPE_HEIGHT,
                "desc": "身高",
                "value": self.height,
                "choiceList": const.MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST,
            },{
                "opType": const.MODEL_USER_OP_TYPE_WEIGHT,
                "desc": "体重",
                "value": self.weight,
                "choiceList": const.MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST,
            },{
                "opType": const.MODEL_USER_OP_TYPE_MONTH_PAY,
                "desc": "月收入",
                "value": self.monthPay,
                "choiceList": const.MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST,
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