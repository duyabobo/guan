#! /usr/bin/env python
# -*- coding: utf-8 -*-

from util import const


class UserHelper(object):  

    def __init__(self, user):
        self.user = user

    @property
    def sexIndex(self):
        try:
            return const.MODEL_USER_SEX_CHOICE_LIST.index(self.user.sex) or const.MODEL_USER_DEFAULT_SEX_INDEX
        except:
            return const.MODEL_USER_DEFAULT_SEX_INDEX

    @property
    def birthYearIndex(self):
        try:
            return const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(self.user.birth_year) or const.MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX
        except:
            return const.MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX

    @property
    def martialStatusIndex(self):
        try:
            return const.MODEL_USER_MARTIAL_STATUS_CHOICE_LIST.index(self.user.martial_status) or const.MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX
        except:
            return const.MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX

    @property
    def heightIndex(self):
        try:
            return const.MODEL_USER_HEIGHT_CHOICE_LIST.index(self.user.height) or const.MODEL_USER_DEFAULT_HEIGHT_INDEX
        except:
            return const.MODEL_USER_DEFAULT_HEIGHT_INDEX

    @property
    def weightIndex(self):
        try:
            return const.MODEL_USER_WEIGHT_CHOICE_LIST.index(self.user.weight) or const.MODEL_USER_DEFAULT_WEIGHT_INDEX
        except:
            return const.MODEL_USER_DEFAULT_WEIGHT_INDEX

    @property
    def monthPayIndex(self):
        try:
            return const.MODEL_USER_MONTH_PAY_CHOICE_LIST.index(self.user.month_pay) or const.MODEL_USER_DEFAULT_MONTH_PAY_INDEX
        except:
            return const.MODEL_USER_DEFAULT_MONTH_PAY_INDEX

    @property
    def educationIndex(self):
        try:
            return const.MODEL_USER_EDUCATION_CHOICE_LIST.index(self.user.education) or const.MODEL_USER_DEFAULT_EDUCATION_INDEX
        except:
            return const.MODEL_USER_DEFAULT_EDUCATION_INDEX

    def getSexInfo(self):
        return {
            "desc": "性别",
            "bindChange": "updateSex",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.user.sex,
            "selectValueIndex": self.sexIndex,
            "choiceList": const.MODEL_USER_SEX_CHOICE_LIST,
        }

    def getBirthYearInfo(self):
        return {
            "desc": "出生年份",
            "bindChange": "updateBirthYear",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.user.birth_year or "",
            "selectValueIndex": self.birthYearIndex,
            "choiceList": const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST,
        }

    def getHeight(self):
        return {
            "desc": "身高(cm)",
            "bindChange": "updateHeight",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.user.height or "",
            "selectValueIndex": self.heightIndex,
            "choiceList": const.MODEL_USER_HEIGHT_CHOICE_LIST,
        }

    def getWeight(self):
        return {
            "desc": "体重(kg)",
            "bindChange": "updateWeight",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.user.weight or "",
            "selectValueIndex": self.weightIndex,
            "choiceList": const.MODEL_USER_WEIGHT_CHOICE_LIST,
        }

    def getMonthPay(self):
        return {
            "desc": "税前月收入(元)",
            "bindChange": "updateMonthPay",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.user.month_pay or "",
            "selectValueIndex": self.monthPayIndex,
            "choiceList": const.MODEL_USER_MONTH_PAY_CHOICE_LIST,
        }

    def getMartialStatus(self):
        return {
            "desc": "婚姻现状",
            "bindChange": "updateMartialStatus",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.user.martial_status,
            "selectValueIndex": self.martialStatusIndex,
            "choiceList": const.MODEL_USER_MARTIAL_STATUS_CHOICE_LIST,
        }

    def getEducation(self):
        return {
            "desc": "学历",
            "bindChange": "updateEducation",
            "pickerType": const.PICKER_TYPE_SELECTOR,
            "value": self.user.education,
            "selectValueIndex": self.educationIndex,
            "choiceList": const.MODEL_USER_EDUCATION_CHOICE_LIST,
        }

    def getUpdateParams(self, opType, valueIndex):
        updateParams = {}
        if opType == const.MODEL_USER_OP_TYPE_SEX and int(valueIndex) != const.MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = const.MODEL_USER_SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_BIRTH_YEAR:
            updateParams['birth_year'] = const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = const.MODEL_USER_MARTIAL_STATUS_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_HEIGHT:
            updateParams['height'] = const.MODEL_USER_HEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_WEIGHT:
            updateParams['weight'] = const.MODEL_USER_WEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_MONTH_PAY:
            updateParams['month_pay'] = const.MODEL_USER_MONTH_PAY_CHOICE_LIST[int(valueIndex)]
        elif opType == const.MODEL_USER_OP_TYPE_EDUCATION:
            updateParams['education'] = const.MODEL_USER_EDUCATION_CHOICE_LIST[int(valueIndex)]
        return updateParams

    @property
    def hasFillFinish(self):
        return self.user.sex != const.MODEL_USER_SEX_CHOICE_LIST[const.MODEL_SEX_UNKNOWN_INDEX] and \
               self.user.birth_year != const.MODEL_USER_BIRTH_YEAR_CHOICE_LIST[const.MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX]  # todo today
