#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.region import RegionModel
from ral.multi_picker import getDataIdAfterColumnChange, getCacheKeyPrefix, multi_picker_config
from util.const.base import ALL_STR
from util.const.education import DEFAULT_MULTI_CHOICE_LIST


class MultiPickerHelperABC(object):  # 扩展用
    def __init__(self, region, opType):
        """
        region是用来计算firstValue的
        """
        self.region = region
        self.opType = opType
        config = multi_picker_config.get(opType, None)
        if config:
            self.dataName = getCacheKeyPrefix(opType)   # education/work
            self.model = config['model']  # EducationModel/WorkModel
            self.firstName = config['firstName']  # school/profession
            self.secondName = config['secondName']  # level/industry
            self.thirdName = config['thirdName']  # major/position

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


class MultiPickerHelper(MultiPickerHelperABC):
    def getDataFromDynamic(self, data, checkDynamicData):
        """结合缓存和数据库，返回用户选择器数据"""
        # 默认值
        firstValue, secondValue, thirdValue = ALL_STR, ALL_STR, ALL_STR
        # 不需要查询动态数据（用户修改了选择器，但是没有提交确认，这些数据缓存在redis，称为动态数据）
        pickerData = getattr(data, self.dataName)
        if pickerData:
            firstValue, secondValue, thirdValue = getattr(pickerData, self.firstName), getattr(pickerData, self.secondName), getattr(pickerData, self.thirdName)
        if not checkDynamicData:
            return firstValue, secondValue, thirdValue
        # 需要查询动态数据
        dataId = getDataIdAfterColumnChange(self.dataName, data.passport_id)
        if not dataId:
            return firstValue, secondValue, thirdValue
        pickerData = self.model.getById(dataId)
        if pickerData:
            firstValue, secondValue, thirdValue = getattr(pickerData, self.firstName), getattr(pickerData, self.secondName), getattr(pickerData, self.thirdName)
        return firstValue, secondValue, thirdValue

    def getFirstChoiceList(self):
        province = self.region.province
        city = self.region.city
        area = self.region.area

        if city == ALL_STR:  # 只选择了省份
            regions = RegionModel.listByProvince(province)
        elif area == ALL_STR:  # 只选择了省份和城市
            regions = RegionModel.listByProvinceAndCity(province, city)
        else:  # 选择了省市区
            regions = RegionModel.listByProvinceAndCityAndArea(province, city, area)

        firstChoiceList = []
        # 一级选择列表
        regionIds = [r.id for r in regions]
        if regionIds:
            _firsts = self.model.getFirstsByRegionids(regionIds)
            _firstSet = set()
            for _f in _firsts:
                f = getattr(_f, self.firstName)
                if f not in _firstSet:
                    _firstSet.add(f)
                    firstChoiceList.append(f)
        return firstChoiceList or DEFAULT_MULTI_CHOICE_LIST

    def getSecondChoiceList(self, first, firstChoiceList):
        # 二级列表
        secondChoiceList = []
        if first in firstChoiceList:  # 没有修改城市
            _seconds = self.model.getSecondsByFirst(first)
            _secondSet = set()
            for _s in _seconds:
                s = getattr(_s, self.secondName)
                if s not in _secondSet:
                    _secondSet.add(s)
                    secondChoiceList.append(s)
        return secondChoiceList or DEFAULT_MULTI_CHOICE_LIST

    def getThirdChoiceList(self, first, second, secondChoiceList):
        # 三级列表
        thirdChoiceList = []
        if second in secondChoiceList:
            _thirds = self.model.getThirdsByFirstAndSecond(first, second)
            _thirdSet = set()
            for _t in _thirds:
                t = getattr(_t, self.thirdName)
                if t not in _thirdSet:
                    _thirdSet.add(t)
                    thirdChoiceList.append(t)
        return thirdChoiceList or DEFAULT_MULTI_CHOICE_LIST

    def getMultiChoiceList(self, firstValue, secondValue, thirdValue):
        if not self.region or self.region.province == ALL_STR:  # 省份都没选择，不让选择多重选择数据
            return [DEFAULT_MULTI_CHOICE_LIST] * 3

        firstChoiceList = self.getFirstChoiceList()
        secondChoiceList = self.getSecondChoiceList(firstValue, firstChoiceList)
        thirdChoiceList = self.getThirdChoiceList(firstValue, secondValue, secondChoiceList)
        return [firstChoiceList, secondChoiceList, thirdChoiceList]

    def getChoiceIdAfterConfirm(self, oldValue, choiceIndexList):
        choiceId = oldValue.id if oldValue else 0

        firstIndex, secondIndex, thirdIndex = choiceIndexList
        if firstIndex < 0 or secondIndex < 0 or thirdIndex < 0:
            return choiceId
        # 查询选择的一级数据值
        firstChoiceList = self.getFirstChoiceList()
        if firstIndex >= len(firstChoiceList):
            return choiceId
        firstValue = firstChoiceList[firstIndex]
        # 查询选择的二级值
        secondChoiceList = self.getSecondChoiceList(firstValue, firstChoiceList)
        if secondIndex >= len(secondChoiceList):
            return choiceId
        secondValue = secondChoiceList[secondIndex]
        # 查询选择的三级值
        thirdChoiceList = self.getThirdChoiceList(firstValue, secondValue, secondChoiceList)
        if thirdIndex >= len(thirdChoiceList):
            return choiceId
        thirdValue = thirdChoiceList[thirdIndex]

        return self.model.getIdByData(self.region.id, firstValue, secondValue, thirdValue)

    def getChoiceIdAfterColumnChanged(self, data, column, choiceValueIndex):
        firstValue, secondValue, thirdValue = self.getDataFromDynamic(data, checkDynamicData=True)
        firstChoiceList, secondChoiceList, thirdChoiceList = self.getMultiChoiceList(firstValue, secondValue, thirdValue)
        if column == 0 and choiceValueIndex < len(firstChoiceList):  # 修改了一级对象
            firstValue = firstChoiceList[choiceValueIndex]
            secondValue = ALL_STR
            thirdValue = ALL_STR
        elif column == 1 and choiceValueIndex < len(secondChoiceList):  # 修改了二级
            secondValue = secondChoiceList[choiceValueIndex]
            thirdValue = ALL_STR
        elif column == 2 and choiceValueIndex < len(thirdChoiceList):  # 修改了三级
            thirdValue = thirdChoiceList[choiceValueIndex]

        return self.model.getIdByData(self.region.id, firstValue, secondValue, thirdValue)
