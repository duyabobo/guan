#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""语音落库前的决定：同性期望整段拒绝；其余维度允许覆盖更新。不访问数据库。"""
from service.common.profile_catalog import (
    ACTIVE_DIMS,
    KIND_RANGE,
    KIND_TEXT,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
)
from util.const.match import MODEL_SEX_FEMALE_INDEX, MODEL_SEX_MALE_INDEX
from util.const.response import RESP_EXPECT_SAME_SEX, RESP_OK

_DIM_BY_KEY = {dim.key: dim for dim in ACTIVE_DIMS}
_KNOWN_SEX = (MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX)


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
    requirement_sex = _sex_from(stored, SCOPE_REQUIREMENT, requirement_values)
    if _rejects_same_sex(own_sex, requirement_sex):
        return ProfileWriteOutcome(msg=RESP_EXPECT_SAME_SEX, rejected=True)

    return ProfileWriteOutcome(
        msg=RESP_OK,
        info_values=_changed_values(SCOPE_INFO, stored, info_values),
        requirement_values=_present_values(SCOPE_REQUIREMENT, requirement_values),
    )


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
