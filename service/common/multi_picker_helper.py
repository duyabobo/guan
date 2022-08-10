#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.education import EducationModel
from model.region import RegionModel
from util.const.base import ALL_STR
from util.const.education import DEFAULT_EDUCATION_MULTI_CHOICE_LIST


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

    def getSchoolChoiceList(self):
        province = self.zeroValue.province
        city = self.zeroValue.city
        area = self.zeroValue.area

        if city == ALL_STR:  # 只选择了省份
            regions = RegionModel.listByProvince(province)
        elif area == ALL_STR:  # 只选择了省份和城市
            regions = RegionModel.listByProvinceAndCity(province, city)
        else:  # 选择了省市区
            regions = RegionModel.listByProvinceAndCityAndArea(province, city, area)

        schoolChoiceList = []
        # 学校选择列表
        regionIds = [r.id for r in regions]
        if regionIds:
            schools = EducationModel.getSchoolsByRegionIds(regionIds)
            _schoolSet = set()
            for s in schools:
                if s.school not in _schoolSet:
                    _schoolSet.add(s.school)
                    schoolChoiceList.append(s.school)
        return schoolChoiceList or DEFAULT_EDUCATION_MULTI_CHOICE_LIST

    def getLevelChoiceList(self, school, schoolChoiceList):
        # 学历列表
        levelChoiceList = []
        if school in schoolChoiceList:  # 没有修改城市
            levels = EducationModel.getLevelsBySchool(school)
            _levelSet = set()
            for l in levels:
                if l.level not in _levelSet:
                    _levelSet.add(l.level)
                    levelChoiceList.append(l.level)
        return levelChoiceList or DEFAULT_EDUCATION_MULTI_CHOICE_LIST

    def getMajorChoiceList(self, school, level, levelChoiceList):
        # 专业列表
        majorChoiceList = []
        if level in levelChoiceList:
            majors = EducationModel.getMajorsBySchoolAndLevel(school, level)
            _majorSet = set()
            for m in majors:
                if m.major not in _majorSet:
                    _majorSet.add(m.major)
                    majorChoiceList.append(m.major)
        return majorChoiceList or DEFAULT_EDUCATION_MULTI_CHOICE_LIST

    def getMultiChoiceList(self, school, level, major):
        if not self.zeroValue or self.zeroValue.province == ALL_STR:  # 省份都没选择，不让选择学校
            return [DEFAULT_EDUCATION_MULTI_CHOICE_LIST] * 3

        schoolChoiceList = self.getSchoolChoiceList()
        levelChoiceList = self.getLevelChoiceList(school, schoolChoiceList)
        majorChoiceList = self.getMajorChoiceList(school, level, levelChoiceList)
        return [schoolChoiceList, levelChoiceList, majorChoiceList]

    def getChoiceIdAfterConfirm(self, oldEducationValue, choiceIndexList):
        if not oldEducationValue:
            return 0
        schoolIndex, levelIndex, majorIndex = choiceIndexList
        # 查询选择的学校值
        schoolChoiceList = self.getSchoolChoiceList()
        if schoolIndex >= len(schoolChoiceList):
            return oldEducationValue.id
        school = schoolChoiceList[schoolIndex]
        # 查询选择的学历值
        levelChoiceList = self.getLevelChoiceList(school, schoolChoiceList)
        if levelIndex >= len(levelChoiceList):
            return oldEducationValue.id
        level = levelChoiceList[levelIndex]
        # 查询选择的专业值
        majorChoiceList = self.getMajorChoiceList(school, level, levelChoiceList)
        if majorIndex >= len(majorChoiceList):
            return oldEducationValue.id
        major = majorChoiceList[majorIndex]
        return EducationModel.getIdByEducation(school, level, major)

    def getChoiceIdAfterColumnChanged(self, oldEducationValue, column, choiceValueIndex):
        if oldEducationValue:
            school, level, major = oldEducationValue.school, oldEducationValue.level, oldEducationValue.major
        else:
            school, level, major = ALL_STR, ALL_STR, ALL_STR

        schoolChoiceList, levelChoiceList, majorChoiceList = self.getMultiChoiceList(school, level, major)
        if column == 0 and choiceValueIndex < len(schoolChoiceList):  # 修改了学校
            school = schoolChoiceList[choiceValueIndex]
            level = ALL_STR
            major = ALL_STR
        elif column == 1 and choiceValueIndex < len(levelChoiceList):  # 修改了学历
            school = oldEducationValue.school
            level = levelChoiceList[choiceValueIndex]
            major = ALL_STR
        elif column == 2 and choiceValueIndex < len(majorChoiceList):  # 修改了专业
            school = oldEducationValue.school
            level = oldEducationValue.level
            major = majorChoiceList[choiceValueIndex]

        return EducationModel.getIdByEducation(school, level, major)
