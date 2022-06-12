#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.match import MATCH_INFO_DICT
from util.const.mini_program import PICKER_TYPE_SELECTOR


class SingleSelector(object):
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
