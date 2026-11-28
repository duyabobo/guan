#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""语音落库前的决定：期望性别按本人性别取反；明确说同性则整段拒绝。不访问数据库。"""
import logging

from service.common.profile_catalog import (
    ACTIVE_DIMS,
    KIND_RANGE,
    KIND_TEXT,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
)
from util.const.match import MODEL_SEX_FEMALE_INDEX, MODEL_SEX_MALE_INDEX
from util.const.response import RESP_EXPECT_SAME_SEX, RESP_OK

logger = logging.getLogger(__name__)

_DIM_BY_KEY = {dim.key: dim for dim in ACTIVE_DIMS}
_KNOWN_SEX = (MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX)
_OPPOSITE_SEX = {
    MODEL_SEX_MALE_INDEX: MODEL_SEX_FEMALE_INDEX,
    MODEL_SEX_FEMALE_INDEX: MODEL_SEX_MALE_INDEX,
}


class ProfileWriteOutcome(object):

    def __init__(self, data=None, msg=None, rejected=False,
                 info_values=None, requirement_values=None):
        self.data = data
        self.msg = msg if msg is not None else RESP_OK
        self.rejected = rejected
        self.info_values = info_values or {}
        self.requirement_values = requirement_values or {}


def decide_profile_write(existing_rows, info_values, requirement_values):
    stored = _index_rows(existing_rows)
    own_sex = _sex_from(stored, SCOPE_INFO, info_values)
    stated_requirement_sex = _stated_sex((requirement_values or {}).get("sex"))
    if _rejects_same_sex(own_sex, stated_requirement_sex):
        return ProfileWriteOutcome(msg=RESP_EXPECT_SAME_SEX, rejected=True)

    requirement_values = _force_opposite_requirement_sex(own_sex, requirement_values)
    return ProfileWriteOutcome(
        msg=RESP_OK,
        info_values=_changed_values(SCOPE_INFO, stored, info_values),
        requirement_values=_present_values(SCOPE_REQUIREMENT, requirement_values),
    )


def _force_opposite_requirement_sex(own_sex, requirement_values):
    """本人性别已知时，期望性别一律取反，不依赖模型是否提到。"""
    opposite = _OPPOSITE_SEX.get(own_sex)
    if opposite is None:
        return requirement_values or {}
    forced = dict(requirement_values or {})
    forced["sex"] = _sex_pack(opposite)
    logger.info("期望性别按本人取反 own=%s requirement=%s", own_sex, opposite)
    return forced


def _sex_pack(sex):
    return {"value_min": sex, "value_max": 0, "value_text": ""}


def _index_rows(existing_rows):
    return {(row.scope, row.dim_key): row for row in existing_rows or []}


def _sex_from(stored, scope, values):
    """本次提到的性别优先，否则用已存值。"""
    incoming = _stated_sex((values or {}).get("sex"))
    if incoming:
        return incoming
    return _stated_sex_from_row(stored.get((scope, "sex")))


def _rejects_same_sex(own_sex, requirement_sex):
    if own_sex not in _KNOWN_SEX or requirement_sex not in _KNOWN_SEX:
        return False
    return own_sex == requirement_sex


def _changed_values(scope, stored, values):
    kept = {}
    for key, packed in _present_values(scope, values).items():
        dim = _DIM_BY_KEY[key]
        if _same_value(dim, scope, stored.get((scope, key)), packed):
            continue
        kept[key] = packed
    return kept


def _present_values(scope, values):
    kept = {}
    for key in _value_keys(values):
        packed = values.get(key)
        dim = _DIM_BY_KEY.get(key)
        if dim is None or not _has_value(dim, scope, packed):
            continue
        kept[key] = packed
    return kept


def _value_keys(values):
    if not values:
        return []
    return list(values.keys())


def _has_value(dim, scope, packed):
    return _kind_value(dim.kind_of(scope), packed) is not None


def _same_value(dim, scope, row, packed):
    if row is None:
        return False
    return _kind_value(dim.kind_of(scope), _row_pack(row)) == _kind_value(dim.kind_of(scope), packed)


def _row_pack(row):
    return {
        "value_min": row.value_min,
        "value_max": row.value_max,
        "value_text": row.value_text,
    }


def _kind_value(kind, packed):
    if not packed:
        return None
    if kind == KIND_TEXT:
        text = str(packed.get("value_text") or "").strip()
        return text or None
    if kind == KIND_RANGE:
        low = int(packed.get("value_min") or 0)
        high = int(packed.get("value_max") or 0)
        if not low and not high:
            return None
        return (low, high)
    number = int(packed.get("value_min") or 0)
    return number or None


def _stated_sex(packed):
    if not packed:
        return 0
    return int(packed.get("value_min") or 0)


def _stated_sex_from_row(row):
    if row is None:
        return 0
    return int(row.value_min or 0)
