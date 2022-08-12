#! /usr/bin/env python
# -*- coding: utf-8 -*-
from service.common.multi_picker_helper import EducationHelper
from util.const.education import DEFAULT_EDUCATION_MULTI_CHOICE_LIST
from util.const.match import *
from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR, PICKER_TYPE_REGION_SELECTOR, \
    PICKER_TYPE_MULTI_EXTRA_SELECTOR

VALUE_TYPE_DICT = {
    OP_TYPE_VERIFY: int,
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
    OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE: int,
}


def selectorFactory(op_type, data, checkDynamicData):
    if op_type == OP_TYPE_VERIFY:
        return SingleSelector("认证类型", VERIFY_CHOICE_LIST[data.verify_type], op_type)
    elif op_type == OP_TYPE_SEX:
        return SingleSelector("性别", SEX_CHOICE_LIST[data.sex], op_type)
    elif op_type == OP_TYPE_BIRTH_YEAR:
        return SingleSelector("出生年份", data.birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT:
        return SingleSelector("身高", data.height, op_type, "(cm)")
    elif op_type == OP_TYPE_WEIGHT:
        return SingleSelector("体重", data.weight, op_type, "(kg)")
    elif op_type == OP_TYPE_MONTH_PAY:
        return SingleSelector("税前月收入", data.month_pay, op_type, "(元)")
    elif op_type == OP_TYPE_MARTIAL_STATUS:
        return SingleSelector("婚姻现状", MARTIAL_STATUS_CHOICE_LIST[data.martial_status], op_type)
    elif op_type == OP_BIRTH_YEAR_PERIOD:
        return MultiSelector("出生年份区间", data.min_birth_year, data.max_birth_year, op_type)
    elif op_type == OP_TYPE_HEIGHT_PERIOD:
        return MultiSelector("身高区间", data.min_height, data.max_height, op_type, "(cm)")
    elif op_type == OP_TYPE_WEIGHT_PERIOD:
        return MultiSelector("体重区间", data.min_weight, data.max_weight, op_type, "(kg)")
    elif op_type == OP_TYPE_MONTH_PAY_PERIOD:
        return MultiSelector("税前月收入", data.min_month_pay, data.max_month_pay, op_type, "(元)")
    elif op_type == OP_TYPE_EDUCATION_MULTI:
        education = data.school, data.level, data.major
        educationDynamic = EducationHelper(data.study_region).getEducationFromDynamic(data, checkDynamicData)
        return MultiSelectorExtra("教育信息", data.study_region, education, educationDynamic, op_type)
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
    def __init__(self, desc, value, bindChange, subDesc=""):
        def _selectValueIndex():  # 值对应的取值范围索引
            try:
                return self.choiceList.index(self.value) or self.defaultIndex
            except:
                return self.defaultIndex

        self.desc = desc  # 名描述
        self.subDesc = subDesc
        self.value = value  # 当前值
        self.fullValue = value
        self.bindChange = bindChange  # 对应小程序的绑定方法
        self.pickerType = PICKER_TYPE_SELECTOR  # 选择器类型：单项

        matchInfo = MATCH_INFO_DICT[self.bindChange]
        self.choiceList = matchInfo['CHOICE_LIST']  # 可选范围列表
        self.defaultIndex = matchInfo['DEFAULT_INDEX']
        self.bindColumnChange = matchInfo['COLUMN_CHANGE_FUNC']  # 小程序解析用的

        self.selectValueIndex = _selectValueIndex()
        self.hasFilled = self.value and self.selectValueIndex != self.defaultIndex  # 当前值是否已完善


class MultiSelector(object):  # 两项选择器
    def __init__(self, desc, fromValue, toValue, bindChange, subDesc=""):
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
        self.subDesc = subDesc
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
    def __init__(self, desc, zeroValue, valueList, valueListDynamic, bindChange):
        """zeroValue用来计算firstValue，firstValue用来计算secondValue, ..."""
        def _selectFirstIndex():
            try:
                return self.multiChoiceList[0].index(firstValue) or self.defaultIndex
            except:
                return self.defaultIndex

        def _selectSecondIndex():
            try:
                return self.multiChoiceList[1].index(secondValue) or self.defaultIndex
            except:
                return self.defaultIndex

        def _selectThirdIndex():
            try:
                return self.multiChoiceList[2].index(thirdValue) or self.defaultIndex
            except:
                return self.defaultIndex

        self.desc = desc
        self.subDesc = ""
        self.pickerType = PICKER_TYPE_MULTI_EXTRA_SELECTOR  # 选择器类型：多项
        self.bindChange = bindChange
        self.firstValue, self.secondValue, self.thirdValue = valueList
        self.fullValue = self.firstValue + self.secondValue + self.thirdValue  # 当前值可读字符串

        firstValue, secondValue, thirdValue = valueListDynamic
        matchInfo = MATCH_INFO_DICT[self.bindChange]
        self.choiceList = matchInfo['CHOICE_LIST']  # 可选范围，废弃
        self.defaultIndex = matchInfo['DEFAULT_INDEX']
        self.bindColumnChange = matchInfo['COLUMN_CHANGE_FUNC']  # 小程序解析用的

        self.multiChoiceList = EducationHelper(zeroValue).getMultiChoiceList(firstValue, secondValue, thirdValue)  # todo 以后扩展，根据bindChange进行工厂函数扩展
        self.multiSelectValueIndex = [_selectFirstIndex(), _selectSecondIndex(), _selectThirdIndex()]
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
        self.subDesc = ""
        self.pickerType = PICKER_TYPE_REGION_SELECTOR  # 选择器类型：地址
        self.region = _getRegin(region)  # 省市区数组
        self.bindChange = bindChange  # 和其他选择器保持一致
        self.bindColumnChange = bindChange
        self.value = _getRegionValue()
        self.fullValue = self.region[0] + self.region[1] + self.region[2]
        self.hasFilled = self.value and self.value != self.customItem  # 当前值是否已完善
