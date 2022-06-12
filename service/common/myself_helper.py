#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.mini_program import PICKER_TYPE_SELECTOR
from util.const.model import *


class MyselfSingleSelector(object):
    """个人信息选择项数据结构：单项选择器"""
    def __init__(self, desc, value, infoStr, bindChange):
        def _selectValueIndex():  # 值对应的取值范围索引
            try:
                return self.choiceList.index(self.value) or self.defaultIndex
            except:
                return self.defaultIndex
        self.desc = desc  # 名描述
        self.value = value  # 当前值
        self.infoStr = infoStr  # 当前值可读字符串
        self.bindChange = bindChange  # 对应小程序的绑定方法
        self.pickerType = PICKER_TYPE_SELECTOR  # 选择器类型：单项
        self.choiceList = {MODEL_USER_OP_TYPE_SEX: MODEL_USER_SEX_CHOICE_LIST}.get(self.bindChange, [])  # 可选范围列表
        self.defaultIndex = {MODEL_USER_OP_TYPE_SEX: MODEL_USER_DEFAULT_SEX_INDEX}.get(self.bindChange, 0)
        self.selectValueIndex = _selectValueIndex()
        self.hasFilled = self.value and self.selectValueIndex != self.defaultIndex  # 当前值是否已完善
        self.bindColumnChange = ''  # 单选无效


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
        return reduce(lambda x, y: x and y, [i.hasFilled for i in informationList])

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
        return MyselfSingleSelector("性别", self.user.sex, self.user.sex, MODEL_USER_OP_TYPE_SEX)  # todo FACTORY

    def getBirthYearInfo(self):
        return MyselfSingleSelector("出生年份", self.user.birth_year, "出生于%d年" % self.user.birth_year, MODEL_USER_OP_TYPE_MARTIAL_STATUS)

    def getHeight(self):
        return MyselfSingleSelector("身高(cm)", self.user.height, "身高%scm" % self.user.height, MODEL_USER_OP_TYPE_WEIGHT)

    def getWeight(self):
        return MyselfSingleSelector("体重(kg)", self.user.weight, "体重%skg" % self.user.weight, MODEL_USER_OP_TYPE_WEIGHT)

    def getMonthPay(self):
        return MyselfSingleSelector("税前月收入(元)", self.user.month_pay, "月收入(税前)%s元" % self.user.month_pay, MODEL_USER_OP_TYPE_MONTH_PAY)

    def getMartialStatus(self):
        return MyselfSingleSelector("婚姻现状", self.user.martial_status, self.user.martial_status, MODEL_USER_OP_TYPE_MARTIAL_STATUS)

    def getEducation(self):
        return MyselfSingleSelector("学历", self.user.education, self.user.education, MODEL_USER_OP_TYPE_EDUCATION)
