#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.requirement import RequirementModel
from model.user import UserModel
from service.common.multi_picker_helper import MultiPickerHelper
from util.const.education import EDUCATION_LEVEL
from util.const.match import *
from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR, PICKER_TYPE_REGION_SELECTOR, \
    PICKER_TYPE_MULTI_EXTRA_SELECTOR

VALUE_TYPE_DICT = {
    # 单项选择器
    OP_TYPE_VERIFY: int,
    OP_TYPE_SEX: int,
    OP_TYPE_BIRTH_YEAR: int,
    OP_TYPE_HEIGHT: int,
    OP_TYPE_WEIGHT: int,
    OP_TYPE_MONTH_PAY: int,
    OP_TYPE_STUDY_FROM_YEAR: int,
    OP_TYPE_EDUCATION_LEVEL: int,
    # 双项选择器
    OP_BIRTH_YEAR_PERIOD: list,
    OP_TYPE_MARTIAL_STATUS: int,
    OP_TYPE_WEIGHT_PERIOD: list,
    OP_TYPE_HEIGHT_PERIOD: list,
    OP_TYPE_MONTH_PAY_PERIOD: list,
    OP_TYPE_HOME_REGION_PERIOD: list,
    OP_TYPE_STUDY_REGION_PERIOD: list,
    OP_TYPE_WORK_REGION_PERIOD: list,
    OP_TYPE_STUDY_FROM_YEAR_PERIOD: list,
    # 地址选择器
    OP_TYPE_HOME_REGION: list,
    OP_TYPE_STUDY_REGION: list,
    OP_TYPE_WORK_REGION: list,
    # 三项选择器
    OP_TYPE_EDUCATION_MULTI: list,
    OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE: int,
    OP_TYPE_WORK_MULTI: list,
    OP_TYPE_WORK_MULTI_COLUMN_CHANGE: int,

}


def selectorFactory(op_type, data, checkDynamicData):
    # 单项选择器
    if op_type == OP_TYPE_VERIFY:
        return SingleSelector("认证类型", VERIFY_CHOICE_LIST[data.verify_type], op_type, choiceRequired=True)
    elif op_type == OP_TYPE_SEX:
        return SingleSelector("性别", SEX_CHOICE_LIST[data.sex], op_type, choiceRequired=True)
    elif op_type == OP_TYPE_BIRTH_YEAR:
        return SingleSelector("出生年份", data.birth_year, op_type, choiceRequired=True)
    elif op_type == OP_TYPE_HEIGHT:
        return SingleSelector("身高", data.height, op_type, "cm", choiceRequired=True)
    elif op_type == OP_TYPE_WEIGHT:
        return SingleSelector("体重", data.weight, op_type, "kg", choiceRequired=True)
    elif op_type == OP_TYPE_MONTH_PAY:
        return SingleSelector("税前月收入", data.month_pay, op_type, "元", choiceRequired=True)
    elif op_type == OP_TYPE_MARTIAL_STATUS:
        return SingleSelector("婚姻现状", MARTIAL_STATUS_CHOICE_LIST[data.martial_status], op_type, choiceRequired=True)
    elif op_type == OP_TYPE_EDUCATION_LEVEL:
        if isinstance(data, UserModel):
            return SingleSelector("最高学历", EDUCATION_LEVEL[data.education_level], op_type, choiceRequired=True)
        elif isinstance(data, RequirementModel):
            return SingleSelector("最低学历", EDUCATION_LEVEL[data.education_level], op_type, choiceRequired=True)
    elif op_type == OP_TYPE_STUDY_FROM_YEAR:
        return SingleSelector("入学时间", data.study_from_year, op_type)
    # 双项选择器
    elif op_type == OP_BIRTH_YEAR_PERIOD:
        return MultiSelector("出生年份区间", data.min_birth_year, data.max_birth_year, op_type, choiceRequired=True)
    elif op_type == OP_TYPE_HEIGHT_PERIOD:
        return MultiSelector("身高区间", data.min_height, data.max_height, op_type, "cm", choiceRequired=True)
    elif op_type == OP_TYPE_WEIGHT_PERIOD:
        return MultiSelector("体重区间", data.min_weight, data.max_weight, op_type, "kg", choiceRequired=True)
    elif op_type == OP_TYPE_MONTH_PAY_PERIOD:
        return MultiSelector("税前月收入", data.min_month_pay, data.max_month_pay, op_type, "元", choiceRequired=True)
    elif op_type == OP_TYPE_STUDY_FROM_YEAR_PERIOD:
        return MultiSelector("入学时间区间", data.min_study_from_year, data.max_study_from_year, op_type)
    # 三项选择器
    elif op_type == OP_TYPE_EDUCATION_MULTI:
        education = data.category, data.disciplines, data.major
        educationDynamic = MultiPickerHelper(op_type).getDataFromDynamic(data, checkDynamicData)
        return MultiSelectorExtra("专业信息", education, educationDynamic, op_type)
    elif op_type == OP_TYPE_WORK_MULTI:
        work = data.profession, data.industry, data.position
        workDynamic = MultiPickerHelper(op_type).getDataFromDynamic(data, checkDynamicData)
        return MultiSelectorExtra("工作信息", work, workDynamic, op_type)
    # 地址选择器
    elif op_type == OP_TYPE_HOME_REGION:
        return RegionSelector("籍贯", data.home_region, op_type)
    elif op_type == OP_TYPE_HOME_REGION_PERIOD:
        return RegionSelector("籍贯范围", data.home_region, op_type)
    elif op_type == OP_TYPE_STUDY_REGION:
        return RegionSelector("学校地址", data.study_region, op_type)
    elif op_type == OP_TYPE_STUDY_REGION_PERIOD:
        return RegionSelector("学校地址范围", data.study_region, op_type)
    elif op_type == OP_TYPE_WORK_REGION:
        return RegionSelector("工作地址", data.work_region, op_type)
    elif op_type == OP_TYPE_WORK_REGION_PERIOD:
        return RegionSelector("工作地址范围", data.work_region, op_type)


class SingleSelector(object):  # 单项选择器
    """个人信息选择项数据结构：单项选择器"""
    def __init__(self, desc, value, bindChange, subDesc="", choiceRequired=False):
        def _selectValueIndex():  # 值对应的取值范围索引
            try:
                return self.choiceList.index(self.value) if self.value in self.choiceList else self.defaultIndex
            except:
                return self.defaultIndex

        self.desc = desc  # 名描述
        self.subDesc = subDesc + " *" if choiceRequired else subDesc
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
    def __init__(self, desc, fromValue, toValue, bindChange, subDesc="", choiceRequired=False):
        def _selectMinIndex():
            try:
                return self.choiceList.index(self.fromValue) if self.fromValue in self.choiceList else self.defaultIndex
            except:
                return self.defaultIndex

        def _selectMaxIndex():
            try:
                return self.choiceList.index(self.toValue) if self.toValue in self.choiceList else self.toValue
            except:
                return self.defaultIndex

        self.desc = desc
        self.subDesc = subDesc + " *" if choiceRequired else subDesc
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
    def __init__(self, desc, valueList, valueListDynamic, bindChange):
        """zeroValue用来计算firstValue，firstValue用来计算secondValue, ..."""
        def _selectFirstIndex():
            try:
                return self.multiChoiceList[0].index(firstValue) if firstValue in self.multiChoiceList[0] else self.defaultIndex
            except:
                return self.defaultIndex

        def _selectSecondIndex():
            try:
                return self.multiChoiceList[1].index(secondValue) if secondValue in self.multiChoiceList[1] else self.defaultIndex
            except:
                return self.defaultIndex

        def _selectThirdIndex():
            try:
                return self.multiChoiceList[2].index(thirdValue) if thirdValue in self.multiChoiceList[2] else self.defaultIndex
            except:
                return self.defaultIndex

        def _getValue():
            if bindChange == OP_TYPE_WORK_MULTI:
                return valueList[2][:12] + '...' if len(valueList[2]) > 12 else valueList[2]
            elif bindChange == OP_TYPE_EDUCATION_MULTI:
                return valueList[0][:12] + '...' if len(valueList[0]) > 12 else valueList[0]
            else:
                return ""

        self.desc = desc
        self.subDesc = ""
        self.pickerType = PICKER_TYPE_MULTI_EXTRA_SELECTOR  # 选择器类型：多项
        self.bindChange = bindChange
        self.firstValue, self.secondValue, self.thirdValue = valueList
        self.value = _getValue()
        self.fullValue = self.firstValue + self.secondValue + self.thirdValue  # 当前值可读字符串

        firstValue, secondValue, thirdValue = valueListDynamic
        matchInfo = MATCH_INFO_DICT[self.bindChange]
        self.choiceList = matchInfo['CHOICE_LIST']  # 可选范围，废弃
        self.defaultIndex = matchInfo['DEFAULT_INDEX']
        self.bindColumnChange = matchInfo['COLUMN_CHANGE_FUNC']  # 小程序解析用的

        multiPickerHelper = MultiPickerHelper(bindChange)
        self.multiChoiceList = multiPickerHelper.getMultiChoiceList(firstValue, secondValue, thirdValue)
        self.multiSelectValueIndex = [_selectFirstIndex(), _selectSecondIndex(), _selectThirdIndex()]
        self.hasFilled = self.firstValue != ALL_STR  # 当前值是否已完善


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
