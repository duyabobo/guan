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


class MyselfSingleSelector(object):
    """个人信息选择项数据结构：单项选择器"""
    def __init__(self, desc, bindChange, choiceList, value, selectValueIndex, infoStr, hasFilled):
        self.desc = desc  # 名描述
        self.bindChange = bindChange  # 对应小程序的绑定方法
        self.pickerType = PICKER_TYPE_SELECTOR  # 选择器类型：单项
        self.choiceList = choiceList  # 可选范围列表
        self.value = value  # 当前值
        self.selectValueIndex = selectValueIndex  # 值对应的取值范围索引
        self.infoStr = infoStr  # 当前值可读字符串
        self.hasFilled = hasFilled  # 当前值是否已完善


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

        return MyselfSingleSelector("性别", MODEL_USER_OP_TYPE_SEX, MODEL_USER_SEX_CHOICE_LIST,
                                    self.user.sex, _sexIndex(), self.user.sex,
                                    self.user.sex != MODEL_USER_SEX_CHOICE_LIST[MODEL_USER_DEFAULT_SEX_INDEX])

    def getBirthYearInfo(self):
        def _birthYearIndex():
            try:
                return MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(
                    self.user.birth_year) or MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX
            except:
                return MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX

        return MyselfSingleSelector("出生年份", MODEL_USER_OP_TYPE_BIRTH_YEAR, MODEL_USER_BIRTH_YEAR_CHOICE_LIST,
                                    self.user.birth_year or "", _birthYearIndex(), "出生于%d年" % self.user.birth_year,
                                    self.user.birth_year != 0)

    def getHeight(self):
        def _heightIndex():
            try:
                return MODEL_USER_HEIGHT_CHOICE_LIST.index(
                    self.user.height) or MODEL_USER_DEFAULT_HEIGHT_INDEX
            except:
                return MODEL_USER_DEFAULT_HEIGHT_INDEX

        return MyselfSingleSelector("身高(cm)", MODEL_USER_OP_TYPE_HEIGHT, MODEL_USER_HEIGHT_CHOICE_LIST,
                                    self.user.height or "", _heightIndex(), "身高%scm" % self.user.height,
                                    self.user.height != 0)

    def getWeight(self):
        def _weightIndex():
            try:
                return MODEL_USER_WEIGHT_CHOICE_LIST.index(
                    self.user.weight) or MODEL_USER_DEFAULT_WEIGHT_INDEX
            except:
                return MODEL_USER_DEFAULT_WEIGHT_INDEX

        return MyselfSingleSelector("体重(kg)", MODEL_USER_OP_TYPE_WEIGHT,MODEL_USER_WEIGHT_CHOICE_LIST,
                                    self.user.weight or "", _weightIndex(), "体重%skg" % self.user.weight,
                                    self.user.weight != 0)

    def getMonthPay(self):
        def _monthPayIndex():
            try:
                return MODEL_USER_MONTH_PAY_CHOICE_LIST.index(
                    self.user.month_pay) or MODEL_USER_DEFAULT_MONTH_PAY_INDEX
            except:
                return MODEL_USER_DEFAULT_MONTH_PAY_INDEX

        return MyselfSingleSelector("税前月收入(元)", MODEL_USER_OP_TYPE_MONTH_PAY, MODEL_USER_MONTH_PAY_CHOICE_LIST,
                                    self.user.month_pay or "", _monthPayIndex(), "月收入(税前)%s元" % self.user.month_pay,
                                    self.user.month_pay != 0)

    def getMartialStatus(self):
        def _martialStatusIndex():
            try:
                return MODEL_USER_MARTIAL_STATUS_CHOICE_LIST.index(
                    self.user.martial_status) or MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX
            except:
                return MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX

        return MyselfSingleSelector("婚姻现状", MODEL_USER_OP_TYPE_MARTIAL_STATUS, MODEL_USER_MARTIAL_STATUS_CHOICE_LIST,
                                    self.user.martial_status, _martialStatusIndex(), self.user.martial_status,
                                    self.user.martial_status != MODEL_USER_MARTIAL_STATUS_CHOICE_LIST[MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX])

    def getEducation(self):
        def _educationIndex():
            try:
                return MODEL_USER_EDUCATION_CHOICE_LIST.index(
                    self.user.education) or MODEL_USER_DEFAULT_EDUCATION_INDEX
            except:
                return MODEL_USER_DEFAULT_EDUCATION_INDEX

        return MyselfSingleSelector("学历", MODEL_USER_OP_TYPE_EDUCATION, MODEL_USER_EDUCATION_CHOICE_LIST,
                                    self.user.education, _educationIndex(), self.user.education,
                                    self.user.education != MODEL_USER_EDUCATION_CHOICE_LIST[MODEL_USER_DEFAULT_EDUCATION_INDEX])
