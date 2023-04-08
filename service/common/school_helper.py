# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2023/4/2 16:54
#  File: school_helper.py
#  Software: PyCharm
from model.region import RegionModel, UNKNOWN_REGION_ID
from model.school import SchoolModel
from ral.cache import checkCache
from util.const.base import EMPTY_STR


class SchoolHelper(object):

    @classmethod
    @checkCache("school_helper:{regionId}")
    def getSortedSchoolList(cls, regionId):  # 算上`未知学校`，缓存，变更数据需刷数据
        def _getSortedSchoolList(regionId):
            regionIds = RegionModel.getRegionIdsByRegionId(regionId)
            regionIds.append(UNKNOWN_REGION_ID)
            return SchoolModel.getSortedList(regionIds)

        schools = _getSortedSchoolList(regionId)
        if len(schools) == 1:  # 本区无大学(len(schools) == 1代表只有一个未知大学)
            region = RegionModel.getById(regionId)
            if region.area != EMPTY_STR:  # 找本市的大学
                regionId = RegionModel.getRegionIdByCity(region.city)
                schools = _getSortedSchoolList(regionId)
            if len(schools) == 1:  # 本市无大学
                if region.city != EMPTY_STR:  # 找本省的大学
                    regionId = RegionModel.getRegionIdByProvince(region.province)
                    schools = _getSortedSchoolList(regionId)
            if len(schools) == 1:  # 本省无大学
                schools = SchoolModel.getAll()  # 找全国的大学
        return schools
