#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""个人资料 / 个人期望的维度目录。

增删维度只改 ACTIVE_DIMS：展示文案、取值形态和抽取字段都在这里。
用户填过的值落在 profile_attr，一个维度一行。
"""
from util.const.match import SEX_CHOICE_LIST

SCOPE_INFO = "info"
SCOPE_REQUIREMENT = "requirement"

KIND_NUMBER = "number"
KIND_RANGE = "range"
KIND_CHOICE = "choice"
KIND_TEXT = "text"

MATCH_RULE_EXACT = "exact"
MATCH_RULE_RANGE = "range"
MATCH_RULE_TEXT = "text"

_EMPTY_PACK = {"value_min": 0, "value_max": 0, "value_text": ""}


def _default_match_rule(requirement_kind):
    if requirement_kind == KIND_RANGE:
        return MATCH_RULE_RANGE
    if requirement_kind == KIND_TEXT:
        return MATCH_RULE_TEXT
    return MATCH_RULE_EXACT


class ProfileDim(object):
    """一个可展示维度。info 与 requirement 共用 key 和 label，取值形态可以不同。"""

    def __init__(self, key, label, unit="", info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
                 info_field="", requirement_field="",
                 requirement_min_field="", requirement_max_field="", choices=None, match_rule=""):
        self.key = key
        self.label = label
        self.unit = unit
        self.info_kind = info_kind
        self.requirement_kind = requirement_kind
        self.match_rule = match_rule or _default_match_rule(requirement_kind)
        self.info_field = info_field
        self.requirement_field = requirement_field
        self.requirement_min_field = requirement_min_field
        self.requirement_max_field = requirement_max_field
        self.choices = choices or []

    def kind_of(self, scope):
        if scope == SCOPE_INFO:
            return self.info_kind
        return self.requirement_kind

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
        info_field="sex", requirement_field="sex",
    ),
    ProfileDim(
        "birth_year", "出生年份",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_field="birth_year",
        requirement_min_field="min_birth_year", requirement_max_field="max_birth_year",
    ),
    ProfileDim(
        "height", "身高", unit="cm",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_field="height",
        requirement_min_field="min_height", requirement_max_field="max_height",
    ),
    ProfileDim(
        "weight", "体重", unit="kg",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_field="weight",
        requirement_min_field="min_weight", requirement_max_field="max_weight",
    ),
    ProfileDim(
        "home_region", "籍贯",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_field="home_region", requirement_field="home_region",
    ),
]

# 加入见面之前，个人信息里这些维度必须有值。
FILL_REQUIRED_INFO_KEYS = ("sex", "birth_year", "height", "weight")


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
