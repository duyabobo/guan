#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.mini_program import PICKER_TYPE_SELECTOR
from util.const.model import *

USER_INFO_GET_FUNCS = [  # 真正生效的用户信息字段获取方法
    'getSexInfo',
    'getBirthYearInfo',
    'getHeight',
    'getWeight',
    'getEducation',
    'getMonthPay',
    'getMartialStatus',
]


class UserHelper(object):

    def __init__(self, user):
        self.user = user

    def getInformationList(self):
        informationList = []
        for func_name in USER_INFO_GET_FUNCS:
            func = self.__getattribute__(func_name)
            informationList.append(func())
        return informationList

    @property
    def hasFillFinish(self):
        informationList = self.getInformationList()
        return reduce(lambda x, y: x and y, [i['hasFilled'] for i in informationList])

    def getUpdateParams(self, opType, valueIndex):
        updateParams = {}
        if opType == MODEL_USER_OP_TYPE_SEX and int(valueIndex) != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = MODEL_USER_SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == MODEL_USER_OP_TYPE_BIRTH_YEAR:
            updateParams['birth_year'] = MODEL_USER_BIRTH_YEAR_CHOICE_LIST[int(valueIndex)]
        elif opType == MODEL_USER_OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = MODEL_USER_MARTIAL_STATUS_CHOICE_LIST[int(valueIndex)]
        elif opType == MODEL_USER_OP_TYPE_HEIGHT:
            updateParams['height'] = MODEL_USER_HEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == MODEL_USER_OP_TYPE_WEIGHT:
            updateParams['weight'] = MODEL_USER_WEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == MODEL_USER_OP_TYPE_MONTH_PAY:
            updateParams['month_pay'] = MODEL_USER_MONTH_PAY_CHOICE_LIST[int(valueIndex)]
        elif opType == MODEL_USER_OP_TYPE_EDUCATION:
            updateParams['education'] = MODEL_USER_EDUCATION_CHOICE_LIST[int(valueIndex)]
        return updateParams

    def getSexInfo(self):
        def _sexIndex():
            try:
                return MODEL_USER_SEX_CHOICE_LIST.index(self.user.sex) or MODEL_USER_DEFAULT_SEX_INDEX
            except:
                return MODEL_USER_DEFAULT_SEX_INDEX

        return {
            "desc": "性别",
            "bindChange": MODEL_USER_OP_TYPE_SEX,
            "pickerType": PICKER_TYPE_SELECTOR,
            "value": self.user.sex,
            "selectValueIndex": _sexIndex(),
            "choiceList": MODEL_USER_SEX_CHOICE_LIST,
            "infoStr": self.user.sex,
            "hasFilled": self.user.sex != MODEL_USER_SEX_CHOICE_LIST[MODEL_USER_DEFAULT_SEX_INDEX],
        }

    def getBirthYearInfo(self):
        def _birthYearIndex():
            try:
                return MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(
                    self.user.birth_year) or MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX
            except:
                return MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX

        return {
            "desc": "出生年份",
            "bindChange": MODEL_USER_OP_TYPE_BIRTH_YEAR,
            "pickerType": PICKER_TYPE_SELECTOR,
            "value": self.user.birth_year or "",
            "selectValueIndex": _birthYearIndex(),
            "choiceList": MODEL_USER_BIRTH_YEAR_CHOICE_LIST,
            "infoStr": "出生于%d年" % self.user.birth_year,
            "hasFilled": self.user.birth_year != 0,
        }

    def getHeight(self):
        def _heightIndex():
            try:
                return MODEL_USER_HEIGHT_CHOICE_LIST.index(
                    self.user.height) or MODEL_USER_DEFAULT_HEIGHT_INDEX
            except:
                return MODEL_USER_DEFAULT_HEIGHT_INDEX

        return {
            "desc": "身高(cm)",
            "bindChange": MODEL_USER_OP_TYPE_HEIGHT,
            "pickerType": PICKER_TYPE_SELECTOR,
            "value": self.user.height or "",
            "selectValueIndex": _heightIndex(),
            "choiceList": MODEL_USER_HEIGHT_CHOICE_LIST,
            "infoStr": "身高%scm" % self.user.height,
            "hasFilled": self.user.height != 0,
        }

    def getWeight(self):
        def _weightIndex():
            try:
                return MODEL_USER_WEIGHT_CHOICE_LIST.index(
                    self.user.weight) or MODEL_USER_DEFAULT_WEIGHT_INDEX
            except:
                return MODEL_USER_DEFAULT_WEIGHT_INDEX

        return {
            "desc": "体重(kg)",
            "bindChange": MODEL_USER_OP_TYPE_WEIGHT,
            "pickerType": PICKER_TYPE_SELECTOR,
            "value": self.user.weight or "",
            "selectValueIndex": _weightIndex(),
            "choiceList": MODEL_USER_WEIGHT_CHOICE_LIST,
            "infoStr": "体重%skg" % self.user.weight,
            "hasFilled": self.user.weight != 0,
        }

    def getMonthPay(self):
        def _monthPayIndex():
            try:
                return MODEL_USER_MONTH_PAY_CHOICE_LIST.index(
                    self.user.month_pay) or MODEL_USER_DEFAULT_MONTH_PAY_INDEX
            except:
                return MODEL_USER_DEFAULT_MONTH_PAY_INDEX

        return {
            "desc": "税前月收入(元)",
            "bindChange": MODEL_USER_OP_TYPE_MONTH_PAY,
            "pickerType": PICKER_TYPE_SELECTOR,
            "value": self.user.month_pay or "",
            "selectValueIndex": _monthPayIndex(),
            "choiceList": MODEL_USER_MONTH_PAY_CHOICE_LIST,
            "infoStr": "月收入(税前)%s元" % self.user.month_pay,
            "hasFilled": self.user.month_pay != 0,
        }

    def getMartialStatus(self):
        def _martialStatusIndex():
            try:
                return MODEL_USER_MARTIAL_STATUS_CHOICE_LIST.index(
                    self.user.martial_status) or MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX
            except:
                return MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX
        return {
            "desc": "婚姻现状",
            "bindChange": MODEL_USER_OP_TYPE_MARTIAL_STATUS,
            "pickerType": PICKER_TYPE_SELECTOR,
            "value": self.user.martial_status,
            "selectValueIndex": _martialStatusIndex(),
            "choiceList": MODEL_USER_MARTIAL_STATUS_CHOICE_LIST,
            "infoStr": self.user.martial_status,
            "hasFilled": self.user.martial_status != MODEL_USER_MARTIAL_STATUS_CHOICE_LIST[MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX],
        }

    def getEducation(self):
        def _educationIndex():
            try:
                return MODEL_USER_EDUCATION_CHOICE_LIST.index(
                    self.user.education) or MODEL_USER_DEFAULT_EDUCATION_INDEX
            except:
                return MODEL_USER_DEFAULT_EDUCATION_INDEX

        return {
            "desc": "学历",
            "bindChange": MODEL_USER_OP_TYPE_EDUCATION,
            "pickerType": PICKER_TYPE_SELECTOR,
            "value": self.user.education,
            "selectValueIndex": _educationIndex(),
            "choiceList": MODEL_USER_EDUCATION_CHOICE_LIST,
            "infoStr": self.user.education,
            "hasFilled": self.user.education != MODEL_USER_EDUCATION_CHOICE_LIST[MODEL_USER_DEFAULT_EDUCATION_INDEX],
        }
