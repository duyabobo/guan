#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.match import *
from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR


def selectorFactory(op_type, data):
    if op_type == OP_TYPE_SEX:
        return SingleSelector("时间（小时）", data.sex, data.sex, op_type)
    elif op_type == OP_TYPE_BIRTH_YEAR:
        return SingleSelector("出生年份", data.birth_year, "出生于%d年" % data.birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT:
        return SingleSelector("周六时间(小时)", data.height, data.height, op_type)
    elif op_type == OP_TYPE_WEIGHT:
        return SingleSelector("周日时间(小时)", data.weight, data.weight, op_type)
    elif op_type == OP_TYPE_MONTH_PAY:
        return SingleSelector("税前月收入(元)", data.month_pay, "月收入(税前)%s元" % data.month_pay, op_type)
    elif op_type == OP_TYPE_MARTIAL_STATUS:
        return SingleSelector("婚姻现状", data.martial_status, data.martial_status, op_type)
    elif op_type == OP_TYPE_EDUCATION:
        return SingleSelector("学历", data.education, data.education, op_type)
    elif op_type == OP_BIRTH_YEAR_PERIOD:
        return MultiSelector("出生年份区间", data.min_birth_year, data.max_birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT_PERIOD:
        return MultiSelector("周六时间区间(小时)", data.min_height, data.max_height, op_type)
    elif op_type == OP_TYPE_WEIGHT_PERIOD:
        return MultiSelector("周日时间区间(小时)", data.min_weight, data.max_weight, op_type)
    elif op_type == OP_TYPE_MONTH_PAY_PERIOD:
        return MultiSelector("税前月收入区间(元)", data.min_month_pay, data.max_month_pay, op_type)
    elif op_type == OP_TYPE_EDUCATION_PERIOD:
        return MultiSelector("学历区间", data.min_education, data.max_education, op_type)


class SingleSelector(object):  # 单项选择器
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

        matchInfo = MATCH_INFO_DICT[self.bindChange]
        self.choiceList = matchInfo['CHOICE_LIST']  # 可选范围列表
        self.defaultIndex = matchInfo['DEFAULT_INDEX']
        self.bindColumnChange = matchInfo['COLUMN_CHANGE_FUNC']  # 小程序解析用的

        self.selectValueIndex = _selectValueIndex()
        self.hasFilled = self.value and self.selectValueIndex != self.defaultIndex  # 当前值是否已完善


class MultiSelector(object):  # 多项选择器
    def __init__(self, desc, fromValue, toValue, bindChange):
        def _selectMinIndex():
            try:
                return self.choiceList.index(self.fromValue) or self.defaultIndex
            except:
                return self.defaultIndex

        def _selectMaxIndex():
            try:
                return self.choiceList.index(self.toValue) or self.toValue
            except:
                return self.defaultIndex

        self.desc = desc
        self.pickerType = PICKER_TYPE_MULTI_SELECTOR  # 选择器类型：多项
        self.bindChange = bindChange
        self.fromValue = fromValue
        self.toValue = toValue

        matchInfo = MATCH_INFO_DICT[self.bindChange]
        self.choiceList = matchInfo['CHOICE_LIST']  # 可选范围列表
        self.defaultIndex = matchInfo['DEFAULT_INDEX']
        self.bindColumnChange = matchInfo['COLUMN_CHANGE_FUNC']  # 小程序解析用的

        self.fromAndToSelectValueIndex = [_selectMinIndex(), _selectMaxIndex()]
        self.fromAndToChoiceList = [self.choiceList, self.choiceList]
