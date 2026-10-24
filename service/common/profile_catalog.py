#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""个人资料 / 个人期望的维度目录。

增删维度只改 ACTIVE_DIMS：展示顺序、文案、取值形态和抽取字段都在这里。
用户填过的值落在 profile_attr，一个维度一行。
"""
import logging

from util.const.match import SEX_CHOICE_LIST

logger = logging.getLogger(__name__)

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

# 下标 0 表示没说。已有下标不要改，库里存的是这个位置。
MARRIAGE_CHOICES = ["未知", "未婚", "离异", "丧偶"]
SMOKE_CHOICES = ["未知", "不吸烟", "偶尔吸烟", "经常吸烟"]
DRINK_CHOICES = ["未知", "不喝酒", "偶尔喝酒", "经常喝酒"]
DEGREE_CHOICES = ["未知", "高中及以下", "专科", "本科", "硕士", "博士"]
HOUSE_CHOICES = ["未知", "未购房", "已购房"]


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
    ProfileDim(
        "live_region", "现居",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_field="live_region", requirement_field="live_region",
    ),
    ProfileDim(
        "job", "职业",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_field="job", requirement_field="job",
    ),
    ProfileDim(
        "income", "收入", unit="元/月",
        info_kind=KIND_NUMBER, requirement_kind=KIND_RANGE,
        info_field="income",
        requirement_min_field="min_income", requirement_max_field="max_income",
    ),
    ProfileDim(
        "school", "毕业学校",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_field="school", requirement_field="school",
    ),
    ProfileDim(
        "first_degree", "第一学历",
        info_kind=KIND_CHOICE, requirement_kind=KIND_CHOICE, choices=DEGREE_CHOICES,
        info_field="first_degree", requirement_field="first_degree",
    ),
    ProfileDim(
        "major", "专业",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_field="major", requirement_field="major",
    ),
    ProfileDim(
        "has_house", "是否购房",
        info_kind=KIND_CHOICE, requirement_kind=KIND_CHOICE, choices=HOUSE_CHOICES,
        info_field="has_house", requirement_field="has_house",
    ),
    ProfileDim(
        "house_region", "在哪里购房",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_field="house_region", requirement_field="house_region",
    ),
    ProfileDim(
        "marriage", "婚姻",
        info_kind=KIND_CHOICE, requirement_kind=KIND_CHOICE, choices=MARRIAGE_CHOICES,
        info_field="marriage", requirement_field="marriage",
    ),
    ProfileDim(
        "smoking", "吸烟",
        info_kind=KIND_CHOICE, requirement_kind=KIND_CHOICE, choices=SMOKE_CHOICES,
        info_field="smoking", requirement_field="smoking",
    ),
    ProfileDim(
        "drinking", "饮酒",
        info_kind=KIND_CHOICE, requirement_kind=KIND_CHOICE, choices=DRINK_CHOICES,
        info_field="drinking", requirement_field="drinking",
    ),
    ProfileDim(
        "hobby", "兴趣",
        info_kind=KIND_TEXT, requirement_kind=KIND_TEXT,
        info_field="hobby", requirement_field="hobby",
    ),
]

# 加入见面之前，个人信息里这些维度必须有值。顺序与上面的展示顺序一致。
FILL_REQUIRED_INFO_KEYS = ("sex", "birth_year", "height", "weight", "home_region")

# 一旦有值就不能再用语音改。冲突时保留旧值，交给人工确认。
LOCKED_INFO_KEYS = ("sex", "birth_year", "height", "home_region")


def extraction_hint():
    """给模型的字段说明，随 ACTIVE_DIMS 变化，避免提示词和目录各写一份。"""
    lines = []
    for dim in ACTIVE_DIMS:
        note = _choice_note(dim)
        if dim.info_field:
            lines.append("%s（个人信息）: %s%s" % (dim.label, dim.info_field, note))
        if dim.requirement_kind == KIND_RANGE and dim.requirement_min_field:
            lines.append("%s（个人期望）: %s / %s" % (
                dim.label, dim.requirement_min_field, dim.requirement_max_field))
        elif dim.requirement_field:
            lines.append("%s（个人期望）: %s%s" % (dim.label, dim.requirement_field, note))
    return "\n".join(lines)


def _choice_note(dim):
    if not dim.choices:
        return ""
    pairs = ["%s=%s" % (index, label) for index, label in enumerate(dim.choices) if index]
    if not pairs:
        return ""
    return "（" + "，".join(pairs) + "）"


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
    return _pack_number(payload, dim.field_of(scope), dim.choices if kind == KIND_CHOICE else None)


def _pack_number(payload, field, choices=None):
    if not field or field not in payload:
        return None
    number = _coerce_number(payload[field], choices, field)
    if number is None:
        return None
    packed = dict(_EMPTY_PACK)
    packed["value_min"] = number
    return packed


def _coerce_number(value, choices, field):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip()
    if not text:
        return 0
    if text.lstrip("-").isdigit():
        return int(text)
    if choices:
        for index, label in enumerate(choices):
            if text == label:
                return index
    logger.info("抽取的选项对不上目录 field=%s", field)
    return None


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
