#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 这里维护活动匹配列表逻辑
from model.education import EducationModel
from model.region import RegionModel
from model.requirement import UNREACHABLE_REQUIREMENT
from model.work import WorkModel
from util.const.education import EDUCATION_LEVEL
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX, BIRTH_YEAR_CHOICE_LIST, HEIGHT_CHOICE_LIST, \
    WEIGHT_CHOICE_LIST, STUDY_FROM_YEAR_CHOICE_LIST, MONTH_PAY_CHOICE_LIST, MODEL_MAIL_TYPE_UNKNOWN, \
    MODEL_MAIL_TYPE_SCHOOL, \
    MODEL_MAIL_TYPE_WORK, REQUIREMENT_MARTIAL_STATUS_CHOICE_LIST, MODEL_MARTIAL_STATUS_UNKNOWN
from util.redis_conn import redisConn
from util.time_cost import timecost

COLUMN_MAP_USER_RANGE = {  # 每个维度对应的取值范围
    "verify_type": [MODEL_MAIL_TYPE_UNKNOWN, MODEL_MAIL_TYPE_SCHOOL, MODEL_MAIL_TYPE_WORK],
    "sex": [MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX],
    "birth_year": BIRTH_YEAR_CHOICE_LIST,
    "height": HEIGHT_CHOICE_LIST,
    "weight": WEIGHT_CHOICE_LIST,
    "home_region_id": RegionModel.getAllRegionIds(),
    "study_from_year": STUDY_FROM_YEAR_CHOICE_LIST,
    "study_region_id": RegionModel.getAllRegionIds(),
    "education_level": range(len(EDUCATION_LEVEL)),
    "education_id": EducationModel.getAllEducationIds(),
    "work_region_id": RegionModel.getAllRegionIds(),
    "work_id": WorkModel.getAllWorkIds(),
    "month_pay": MONTH_PAY_CHOICE_LIST,
    "martial_status": range(len(REQUIREMENT_MARTIAL_STATUS_CHOICE_LIST)),
}


COLUMN_MAP_RERQUIREMENT_RANGE_FUNC = {
    "verify_type": lambda x: [getattr(x, "verify_type")],
    "sex": lambda x: [getattr(x, "sex")],
    "birth_year": lambda x: range(getattr(x, "min_birth_year"), getattr(x, "max_birth_year")),
    "height": lambda x: range(getattr(x, "min_height"), getattr(x, "max_height")),
    "weight": lambda x: range(getattr(x, "min_weight"), getattr(x, "max_weight")),
    "home_region_id": lambda x: RegionModel.getRegionIdsByRegionId(getattr(x, "home_region_id")),
    "study_from_year": lambda x: range(getattr(x, "min_study_from_year"), getattr(x, "max_study_from_year")),
    "study_region_id": lambda x: RegionModel.getRegionIdsByRegionId(getattr(x, "home_region_id")),
    "education_level": lambda x: [getattr(x, "education_level"), getattr(x, "education_level")],
    "education_id": lambda x: EducationModel.getEducationIdsByEducationId(getattr(x, "education_id")),
    "work_region_id": lambda x: RegionModel.getRegionIdsByRegionId(getattr(x, "home_region_id")),
    "work_id": lambda x: WorkModel.getWorkIdsByWorkId(getattr(x, "work_id")),
    "month_pay": lambda x: range(getattr(x, "min_month_pay"), getattr(x, "max_month_pay")),
    "martial_status": lambda x: range(getattr(x, "martial_status")+1)
    if getattr(x, "martial_status") != MODEL_MARTIAL_STATUS_UNKNOWN
    else range(len(REQUIREMENT_MARTIAL_STATUS_CHOICE_LIST)),
}


def getKey(columnName, columnValue):
    return "%s:%s:activityIdSet" % (columnName, str(columnValue))


def addActivityId(pipeline, key, activityId):
    pipeline.sadd(key, activityId)


def remActivityId(pipeline, key, activityId):
    pipeline.srem(key, activityId)


# 新增活动，全覆盖key填充
def addByActivity(activityId):
    pipeline = redisConn.pipeline()
    for columnName, valueRange in COLUMN_MAP_USER_RANGE.items():
        for v in valueRange:
            addActivityId(pipeline, getKey(columnName, v), activityId)
    pipeline.execute()


# 修改期望
def changeByRequirement(activityId, oldRequirement, newRequirement):
    def _getRequirementRange(requirement):
        if requirement is None:  # 期望为空
            requirementRange = COLUMN_MAP_USER_RANGE[columnName]
        elif requirement is UNREACHABLE_REQUIREMENT:  # 期望不可达
            requirementRange = set()
        else:
            requirementRange = requirementValueRangeFunc(requirement)
        return requirementRange

    pipeline = redisConn.pipeline()
    for columnName, requirementValueRangeFunc in COLUMN_MAP_RERQUIREMENT_RANGE_FUNC.items():
        oldRequirementRange = _getRequirementRange(oldRequirement)
        newRequirementRange = _getRequirementRange(newRequirement)
        for v in set(newRequirementRange) - set(oldRequirementRange):
            addActivityId(pipeline, getKey(columnName, v), activityId)
        for v in set(oldRequirementRange) - set(newRequirementRange):
            remActivityId(pipeline, getKey(columnName, v), activityId)
    pipeline.execute()

    
# 清空活动(活动过期处理)
def cleanByActivity(activityId):
    pipeline = redisConn.pipeline()
    for columnName, valueRange in COLUMN_MAP_USER_RANGE.items():
        for v in valueRange:
            remActivityId(pipeline, getKey(columnName, v), activityId)
    pipeline.execute()


# 查询某个用户匹配的活动id集合
@timecost
def getMatchedActivityIds(user):
    matchedKeys = []
    for columnName in COLUMN_MAP_USER_RANGE:
        matchedKeys.append(getKey(columnName, getattr(user, columnName)))
    return redisConn.sunion(matchedKeys)
