#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.education import DEFAULT_EDUCATION_MULTI_CHOICE_LIST
from util.const.match import *
from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR, PICKER_TYPE_REGION_SELECTOR, \
    PICKER_TYPE_MULTI_EXTRA_SELECTOR

VALUE_TYPE_DICT = {
    OP_TYPE_SEX: int,
    OP_TYPE_BIRTH_YEAR: int,
    OP_TYPE_HEIGHT: int,
    OP_TYPE_WEIGHT: int,
    OP_TYPE_MONTH_PAY: int,
    OP_BIRTH_YEAR_PERIOD: list,
    OP_TYPE_MARTIAL_STATUS: int,
    OP_TYPE_WEIGHT_PERIOD: list,
    OP_TYPE_HEIGHT_PERIOD: list,
    OP_TYPE_MONTH_PAY_PERIOD: list,
    OP_TYPE_HOME_REGION_PERIOD: list,
    OP_TYPE_STUDY_REGION_PERIOD: list,
    OP_TYPE_HOME_REGION: list,
    OP_TYPE_STUDY_REGION: list,
    OP_TYPE_EDUCATION_MULTI: list,
}


def selectorFactory(op_type, data):
    if op_type == OP_TYPE_SEX:
        return SingleSelector("性别", data.sex, data.sex, op_type)
    elif op_type == OP_TYPE_BIRTH_YEAR:
        return SingleSelector("出生年份", data.birth_year, "出生于%d年" % data.birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT:
        return SingleSelector("身高(cm)", data.height, "身高%scm" % data.height, op_type)
    elif op_type == OP_TYPE_WEIGHT:
        return SingleSelector("体重(kg)", data.weight, "体重%skg" % data.weight, op_type)
    elif op_type == OP_TYPE_MONTH_PAY:
        return SingleSelector("税前月收入(元)", data.month_pay, "月收入(税前)%s元" % data.month_pay, op_type)
    elif op_type == OP_TYPE_MARTIAL_STATUS:
        return SingleSelector("婚姻现状", data.martial_status, data.martial_status, op_type)
    elif op_type == OP_BIRTH_YEAR_PERIOD:
        return MultiSelector("出生年份区间", data.min_birth_year, data.max_birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT_PERIOD:
        return MultiSelector("身高区间(cm)", data.min_height, data.max_height, op_type)
    elif op_type == OP_TYPE_WEIGHT_PERIOD:
        return MultiSelector("体重区间(kg)", data.min_weight, data.max_weight, op_type)
    elif op_type == OP_TYPE_MONTH_PAY_PERIOD:
        return MultiSelector("税前月收入区间(元)", data.min_month_pay, data.max_month_pay, op_type)
    elif op_type == OP_TYPE_EDUCATION_MULTI:
        return MultiSelectorExtra("教育信息", data.study_region.city, data.school, data.level, data.major, op_type)
    elif op_type == OP_TYPE_HOME_REGION_PERIOD:
        return RegionSelector("籍贯范围", data.home_region, op_type)
    elif op_type == OP_TYPE_STUDY_REGION_PERIOD:
        return RegionSelector("学校地址范围", data.study_region, op_type)
    elif op_type == OP_TYPE_HOME_REGION:
        return RegionSelector("籍贯", data.home_region, op_type)
    elif op_type == OP_TYPE_STUDY_REGION:
        return RegionSelector("学校地址", data.study_region, op_type)


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


class MultiSelector(object):  # 两项选择器
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


class MultiSelectorExtra(object):  # 三项选择器
    def __init__(self, desc, zeroValue, firstValue, secondValue, thirdValue, bindChange):
        """zeroValue用来计算firstValue，firstValue用来计算secondValue, ..."""
        def _firstChoiceList():
            zeroMapFirstChoiceList = {
                z[0]: [f[0] for f in z[1:]] for z in zeroList
            }
            return zeroMapFirstChoiceList.get(zeroValue, DEFAULT_EDUCATION_MULTI_CHOICE_LIST)

        def _secondChoiceList():
            firstMapSecondChoiceList = {
                f[0]: f[1:] for f in firstList
            }
            return firstMapSecondChoiceList.get(firstValue, DEFAULT_EDUCATION_MULTI_CHOICE_LIST)

        def _thirdChoiceList():
            secondMapThirdChoiceList = {
                s[0]: s[1] for s in secondList
            }
            return secondMapThirdChoiceList.get(secondValue, DEFAULT_EDUCATION_MULTI_CHOICE_LIST)

        def _selectFirstIndex():
            try:
                return self.firstChoiceList.index(self.firstValue) or self.defaultIndex
            except:
                return self.defaultIndex

        def _selectSecondIndex():
            try:
                return self.firstChoiceList.index(self.secondValue) or self.defaultIndex
            except:
                return self.defaultIndex

        def _selectThirdIndex():
            try:
                return self.firstChoiceList.index(self.thirdValue) or self.defaultIndex
            except:
                return self.defaultIndex

        self.desc = desc
        self.pickerType = PICKER_TYPE_MULTI_EXTRA_SELECTOR  # 选择器类型：多项
        self.bindChange = bindChange
        self.firstValue = firstValue
        self.secondValue = secondValue
        self.thirdValue = thirdValue

        matchInfo = MATCH_INFO_DICT[self.bindChange]
        self.choiceList = matchInfo['CHOICE_LIST']  # 可选范围
        self.defaultIndex = matchInfo['DEFAULT_INDEX']
        self.bindColumnChange = matchInfo['COLUMN_CHANGE_FUNC']  # 小程序解析用的

        zeroList = self.choiceList
        firstList = DEFAULT_EDUCATION_MULTI_CHOICE_LIST
        for z in zeroList:
            if z[0] == zeroValue:
                firstList = z[1:]
        secondList = DEFAULT_EDUCATION_MULTI_CHOICE_LIST
        for f in firstList:
            if f[0] == firstValue:
                secondList = f[1:]

        self.firstChoiceList = _firstChoiceList()
        self.secondChoiceList = _secondChoiceList()
        self.thirdChoiceList = _thirdChoiceList()
        self.multiSelectValueIndex = [_selectFirstIndex(), _selectSecondIndex(), _selectThirdIndex()]
        self.multiChoiceList = [self.firstChoiceList, self.secondChoiceList, self.thirdChoiceList]
        self.hasFilled = [self.firstValue] != DEFAULT_EDUCATION_MULTI_CHOICE_LIST  # 当前值是否已完善


class RegionSelector(object):  # 省市区选择器
    def __init__(self, desc, region, bindChange):

        def _getRegin(region):
            """返回['广东省', '广州市', '海珠区']"""
            return [region.province, region.city, region.area] if region else [self.customItem, self.customItem, self.customItem]

        def _getRegionValue():
            """展示的已选省市区文案结果"""
            v = self.customItem
            for r in self.region:
                if r == self.customItem:
                    continue
                else:
                    v = r
            return v[:10]

        self.customItem = ALL_STR  # 可为每一列的顶部添加一个自定义的项
        self.desc = desc
        self.pickerType = PICKER_TYPE_REGION_SELECTOR  # 选择器类型：地址
        self.region = _getRegin(region)  # 省市区数组
        self.bindColumnChange = bindChange
        self.value = _getRegionValue()
        self.hasFilled = self.value and self.value != self.customItem  # 当前值是否已完善
