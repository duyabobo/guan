#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""个人资料 / 个人期望的维度目录。

增删维度只改 ACTIVE_DIMS：展示文案、取值形态、和旧选择器的对应关系都在这里。
用户填过的值落在 profile_attr，一个维度一行，不给 user / requirement 加字段。
"""
from util.const.education import EDUCATION_LEVEL
from util.const.match import (
    OP_BIRTH_YEAR_PERIOD,
    OP_TYPE_BIRTH_YEAR,
    OP_TYPE_EDUCATION_LEVEL,
    OP_TYPE_EDUCATION_MULTI,
    OP_TYPE_HEIGHT,
    OP_TYPE_HEIGHT_PERIOD,
    OP_TYPE_HOME_REGION,
    OP_TYPE_HOME_REGION_PERIOD,
    OP_TYPE_SEX,
    OP_TYPE_STUDY_FROM_YEAR,
    OP_TYPE_STUDY_FROM_YEAR_PERIOD,
    OP_TYPE_STUDY_REGION,
    OP_TYPE_STUDY_REGION_PERIOD,
    OP_TYPE_STUDY_SCHOOL,
    OP_TYPE_WEIGHT,
    OP_TYPE_WEIGHT_PERIOD,
    SEX_CHOICE_LIST,
)

SCOPE_INFO = "info"
SCOPE_REQUIREMENT = "requirement"

KIND_NUMBER = "number"
KIND_RANGE = "range"
KIND_CHOICE = "choice"
KIND_TEXT = "text"

_EMPTY_PACK = {"value_min": 0, "value_max": 0, "value_text": ""}


class ProfileDim(object):
    """一个可展示维度。info 与 requirement 共用 key 和 label，取值形态可以不同。"""

    def __init__(self, key, label, unit="", info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
                 info_op="", requirement_op="", info_field="", requirement_field="",
                 requirement_min_field="", requirement_max_field="", choices=None):
        self.key = key
        self.label = label
        self.unit = unit
        self.info_kind = info_kind
        self.requirement_kind = requirement_kind
        self.info_op = info_op
        self.requirement_op = requirement_op
        self.info_field = info_field
        self.requirement_field = requirement_field
        self.requirement_min_field = requirement_min_field
        self.requirement_max_field = requirement_max_field
        self.choices = choices or []

    def kind_of(self, scope):
        if scope == SCOPE_INFO:
            return self.info_kind
        return self.requirement_kind

    def op_of(self, scope):
        if scope == SCOPE_INFO:
            return self.info_op
        return self.requirement_op

    def field_of(self, scope):
        if scope == SCOPE_INFO:
            return self.info_field
        return self.requirement_field

    def range_fields_of(self, scope):
        if scope == SCOPE_REQUIREMENT:
            return self.requirement_min_field, self.requirement_max_field
        return "", ""


# 展示顺序即列表顺序。从这里删掉的维度不再下发给小程序。
ACTIVE_DIMS = [
    ProfileDim(
        "sex", "性别",
        info_kind=KIND_CHOICE, requirement_kind=KIND_CHOICE, choices=SEX_CHOICE_LIST,
        info_op=OP_TYPE_SEX, requirement_op=OP_TYPE_SEX,
        info_field="sex", requirement_field="sex",
    ),
    ProfileDim(
        "birth_year", "出生年份",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_op=OP_TYPE_BIRTH_YEAR, requirement_op=OP_BIRTH_YEAR_PERIOD,
        info_field="birth_year",
        requirement_min_field="min_birth_year", requirement_max_field="max_birth_year",
    ),
    ProfileDim(
        "height", "身高", unit="cm",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_op=OP_TYPE_HEIGHT, requirement_op=OP_TYPE_HEIGHT_PERIOD,
        info_field="height",
        requirement_min_field="min_height", requirement_max_field="max_height",
    ),
    ProfileDim(
        "weight", "体重", unit="kg",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_op=OP_TYPE_WEIGHT, requirement_op=OP_TYPE_WEIGHT_PERIOD,
        info_field="weight",
        requirement_min_field="min_weight", requirement_max_field="max_weight",
    ),
    ProfileDim(
        "home_region", "籍贯",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_op=OP_TYPE_HOME_REGION, requirement_op=OP_TYPE_HOME_REGION_PERIOD,
    ),
    ProfileDim(
        "education_level", "学历",
        info_kind=KIND_CHOICE, requirement_kind=KIND_CHOICE, choices=EDUCATION_LEVEL,
        info_op=OP_TYPE_EDUCATION_LEVEL, requirement_op=OP_TYPE_EDUCATION_LEVEL,
        info_field="education_level", requirement_field="education_level",
    ),
    ProfileDim(
        "study_region", "学校地址",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_op=OP_TYPE_STUDY_REGION, requirement_op=OP_TYPE_STUDY_REGION_PERIOD,
    ),
    ProfileDim(
        "school", "学校",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_op=OP_TYPE_STUDY_SCHOOL, requirement_op=OP_TYPE_STUDY_SCHOOL,
    ),
    ProfileDim(
        "study_from_year", "入学时间",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_op=OP_TYPE_STUDY_FROM_YEAR, requirement_op=OP_TYPE_STUDY_FROM_YEAR_PERIOD,
        info_field="study_from_year",
        requirement_min_field="min_study_from_year", requirement_max_field="max_study_from_year",
    ),
    ProfileDim(
        "education", "专业",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_op=OP_TYPE_EDUCATION_MULTI, requirement_op=OP_TYPE_EDUCATION_MULTI,
    ),
]

_DIM_BY_KEY = {dim.key: dim for dim in ACTIVE_DIMS}

# 加入见面之前，个人信息里这些维度必须有值。
FILL_REQUIRED_INFO_KEYS = ("sex", "birth_year", "height", "weight", "education_level")


def get_dim(key):
    return _DIM_BY_KEY.get(key)


def extraction_hint():
    """给模型的字段说明，随 ACTIVE_DIMS 变化，避免提示词和目录各写一份。"""
    lines = []
    for dim in ACTIVE_DIMS:
        if dim.info_field:
            lines.append("%s（个人信息）: %s" % (dim.label, dim.info_field))
        if dim.requirement_kind == KIND_RANGE and dim.requirement_min_field:
            lines.append("%s（个人期望）: %s / %s" % (
                dim.label, dim.requirement_min_field, dim.requirement_max_field))
        elif dim.requirement_field:
            lines.append("%s（个人期望）: %s" % (dim.label, dim.requirement_field))
    return "\n".join(lines)


def values_from_payload(scope, payload):
    """把一次提取结果收成 {dim_key: {value_min, value_max, value_text}}。没提到的维度不出现。"""
    if not payload:
        return {}
    values = {}
    for dim in ACTIVE_DIMS:
        packed = _pack_dim(dim, scope, payload)
        if packed is not None:
            values[dim.key] = packed
    return values


def _pack_dim(dim, scope, payload):
    kind = dim.kind_of(scope)
    if kind == KIND_RANGE:
        return _pack_range(payload, *dim.range_fields_of(scope))
    if kind == KIND_TEXT:
        return _pack_text(payload, dim.field_of(scope))
    return _pack_number(payload, dim.field_of(scope))


def _pack_number(payload, field):
    if not field or field not in payload:
        return None
    packed = dict(_EMPTY_PACK)
    packed["value_min"] = int(payload[field] or 0)
    return packed


def _pack_range(payload, min_field, max_field):
    if not min_field and not max_field:
        return None
    if min_field not in payload and max_field not in payload:
        return None
    packed = dict(_EMPTY_PACK)
    packed["value_min"] = int(payload.get(min_field) or 0)
    packed["value_max"] = int(payload.get(max_field) or 0)
    return packed


def _pack_text(payload, field):
    if not field or field not in payload:
        return None
    packed = dict(_EMPTY_PACK)
    packed["value_text"] = str(payload[field] or "")
    return packed
