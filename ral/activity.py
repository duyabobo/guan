#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 这里维护活动匹配列表逻辑
from model.education import EducationModel
from model.region import RegionModel
from model.work import WorkModel
from util.const.education import EDUCATION_LEVEL
from util.const.match import MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX, BIRTH_YEAR_CHOICE_LIST, HEIGHT_CHOICE_LIST, \
    WEIGHT_CHOICE_LIST, STUDY_FROM_YEAR_CHOICE_LIST, MONTH_PAY_CHOICE_LIST, MODEL_MARTIAL_STATUS_UNKNOWN, \
    MODEL_MARTIAL_STATUS_NO_MARRY, MODEL_MARTIAL_STATUS_BREAK, MODEL_MAIL_TYPE_UNKNOWN, MODEL_MAIL_TYPE_SCHOOL, \
    MODEL_MAIL_TYPE_WORK
from util.redis_conn import redisConn


COLUMN_MAP_USER_RANGE = {  # 每个维度对应的取值范围
    "mail_type": [MODEL_MAIL_TYPE_UNKNOWN, MODEL_MAIL_TYPE_SCHOOL, MODEL_MAIL_TYPE_WORK],
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
    "martial_status": [MODEL_MARTIAL_STATUS_UNKNOWN, MODEL_MARTIAL_STATUS_NO_MARRY, MODEL_MARTIAL_STATUS_BREAK],
}


COLUMN_MAP_RERQUIREMENT_RANGE_FUNC = {
    "mail_type": lambda x: getattr(x, "verify_type"),
    "sex": lambda x: getattr(x, "sex"),
    "birth_year": lambda x: range(getattr(x, "min_birth_year"), getattr(x, "max_birth_year")),
    "height": lambda x: range(getattr(x, "min_height"), getattr(x, "max_height")),
    "weight": lambda x: range(getattr(x, "min_weight"), getattr(x, "max_weight")),
    "home_region_id": lambda x: RegionModel.getRegionIdsByRegionId(getattr(x, "home_region_id")),
    "study_from_year": lambda x: range(getattr(x, "min_study_from_year"), getattr(x, "max_study_from_year")),
    "study_region_id": lambda x: RegionModel.getRegionIdsByRegionId(getattr(x, "home_region_id")),
    "education_level": lambda x: getattr(x, "education_level"),
    "education_id": lambda x: EducationModel.getEducationIdsByEducationId(getattr(x, "education_id")),
    "work_region_id": lambda x: RegionModel.getRegionIdsByRegionId(getattr(x, "home_region_id")),
    "work_id": lambda x: WorkModel.getWorkIdsByWorkId(getattr(x, "work_id")),
    "month_pay": lambda x: range(getattr(x, "min_month_pay"), getattr(x, "max_month_pay")),
    "martial_status": lambda x: getattr(x, "martial_status"),
}


def getKey(columnName, columnValue):
    return "%s:%s:activityIdSet" % (columnName, str(columnValue))


def addActivityId(pipeline, key, activityId):
    pipeline.sadd(key, activityId)


def remActivityId(pipeline, key, activityId):
    pipeline.srem(key, activityId)


# 新增活动，全覆盖key填充
def addActivity(activity):
    pipeline = redisConn.pipeline()
    for columnName, valueRange in COLUMN_MAP_USER_RANGE.items():
        for v in valueRange:
            addActivityId(pipeline, getKey(columnName, v), activity.id)
    pipeline.execute()


# 发起邀请，修剪
def inviteActivity(activity, requirement):
    pipeline = redisConn.pipeline()
    for columnName, userValueRange in COLUMN_MAP_USER_RANGE.items():
        requirementValueRange = COLUMN_MAP_RERQUIREMENT_RANGE_FUNC[columnName](requirement)
        for v in set(userValueRange) - set(requirementValueRange):
            remActivityId(pipeline, getKey(columnName, v), activity.id)
    pipeline.execute()


# 取消邀请
def uninviteActivity(activity, requirement):
    pipeline = redisConn.pipeline()
    for columnName, userValueRange in COLUMN_MAP_USER_RANGE.items():
        requirementValueRange = COLUMN_MAP_RERQUIREMENT_RANGE_FUNC[columnName](requirement)
        for v in set(userValueRange) - set(requirementValueRange):
            addActivityId(pipeline, getKey(columnName, v), activity.id)
    pipeline.execute()


# 接受邀请
def acceptActivity(activity, requirement):
    pipeline = redisConn.pipeline()
    for columnName, requirementValueRangeFunc in COLUMN_MAP_RERQUIREMENT_RANGE_FUNC.items():
        for v in requirementValueRangeFunc(requirement):
            remActivityId(pipeline, getKey(columnName, v), activity.id)
    pipeline.execute()


# 取消接受
def unacceptActivity(activity, requirement):
    pipeline = redisConn.pipeline()
    for columnName, requirementValueRangeFunc in COLUMN_MAP_RERQUIREMENT_RANGE_FUNC.items():
        for v in requirementValueRangeFunc(requirement):
            addActivityId(pipeline, getKey(columnName, v), activity.id)
    pipeline.execute()


# 发起邀请后修改期望
def changeRequirement(activity, oldRequirement, newRequirement):
    pipeline = redisConn.pipeline()
    for columnName, requirementValueRangeFunc in COLUMN_MAP_RERQUIREMENT_RANGE_FUNC.items():
        oldRequirementRange = requirementValueRangeFunc(oldRequirement)
        newRequirementRange = requirementValueRangeFunc(newRequirement)
        for v in set(newRequirementRange) - set(oldRequirementRange):
            addActivityId(pipeline, getKey(columnName, v), activity.id)
        for v in set(oldRequirementRange) - set(newRequirementRange):
            remActivityId(pipeline, getKey(columnName, v), activity.id)
    pipeline.execute()
