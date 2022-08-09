#! /usr/bin/env python
# -*- coding: utf-8 -*-

class MultiPickerHelper(object):  # 扩展用
    def __init__(self, zeroValue):
        """
        zeroValue是用来计算firstValue的
        """
        self.zeroValue = zeroValue

    def getMultiChoiceList(self, firstValue, secondValue, thirdValue):  # 查询多重选择列表
        """返回一个长度3的二维数组"""
        return []

    def getChoiceIdAfterColumnChanged(self, oldValue, column, valueIndex):  # 修改多重选择列表
        """用户修改了多重选择器的某个列，返回对应数据库多重选择对象的id
        # 1，拿到旧的教育信息
        # 2，查询多重选择器列表（保证education表不会修改，不然查询和更新时，可能valueIndex对应的value不一样）
        # 3，根据改后的column/value（index），映射第2步计算的多重选择列表，计算变更后的信息。变更列前面的值（照旧）/变更当前列的值/变更后面列的值（默认值）
        # 4，根据变更后的信息（firstValue, secondValue, thirdValue值），查询对应多重选择对象的id。
        """
        return 0


class EducationHelper(MultiPickerHelper):

    def getMultiChoiceList(self, firstValue, secondValue, thirdValue):
        return []

    def getChoiceIdAfterColumnChanged(self, oldValue, column, valueIndex):
        return 0
