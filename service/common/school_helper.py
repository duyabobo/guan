# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2023/4/2 16:54
#  File: school_helper.py
#  Software: PyCharm
from model.region import RegionModel, UNKNOWN_REGION_ID
from model.school import SchoolModel, UNKNOWN_SCHOOL_ID
from ral.cache import checkCache
from util.const.base import EMPTY_STR


def _only_unknown_school(schools):
    """没有真实学校，或列表里只剩「未知学校」占位。"""
    if not schools:
        return True
    return len(schools) == 1 and schools[0].id == UNKNOWN_SCHOOL_ID


class SchoolHelper(object):

    @classmethod
    @checkCache("school_helper:{regionId}")
    def getSortedSchoolList(cls, regionId):  # 算上`未知学校`，缓存，变更数据需刷数据
        def _getSortedSchoolList(region_id):
            region_ids = RegionModel.getRegionIdsByRegionId(region_id)
            region_ids.append(UNKNOWN_REGION_ID)
            return SchoolModel.getSortedList(region_ids)

        schools = _getSortedSchoolList(regionId)
        if not _only_unknown_school(schools):
            return schools

        region = RegionModel.getById(regionId)
        if region and region.area != EMPTY_STR:
            schools = _getSortedSchoolList(RegionModel.getRegionIdByCity(region.city))
        if region and _only_unknown_school(schools) and region.city != EMPTY_STR:
            schools = _getSortedSchoolList(RegionModel.getRegionIdByProvince(region.province))
        if _only_unknown_school(schools):
            schools = SchoolModel.getAll()
        return schools
