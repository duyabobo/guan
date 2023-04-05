# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2023/4/2 16:54
#  File: school_helper.py
#  Software: PyCharm
from model.region import RegionModel, UNKNOWN_REGION_ID
from model.school import SchoolModel
from ral.cache import checkCache


class SchoolHelper(object):

    @classmethod
    @checkCache("school_helper:{regionId}")
    def getSortedSchoolList(cls, regionId):  # 算上`未知学校`，缓存，变更数据需刷数据
        regionIds = RegionModel.getRegionIdsByRegionId(regionId)
        regionIds.append(UNKNOWN_REGION_ID)
        return SchoolModel.getSortedList(regionIds)
