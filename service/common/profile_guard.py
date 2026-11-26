#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""语音落库前的决定：锁定资料冲突时留旧值，同性期望整段拒绝。不访问数据库。"""
from service.common.profile_catalog import (
    ACTIVE_DIMS,
    KIND_RANGE,
    KIND_TEXT,
    LOCKED_INFO_KEYS,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
)
from util.const.match import MODEL_SEX_FEMALE_INDEX, MODEL_SEX_MALE_INDEX
from util.const.response import RESP_EXPECT_SAME_SEX, RESP_OK, profile_conflict_msg

_DIM_BY_KEY = {dim.key: dim for dim in ACTIVE_DIMS}
_KNOWN_SEX = (MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX)
_LOCKED_INFO = frozenset(LOCKED_INFO_KEYS)


class ProfileWriteOutcome(object):

    def __init__(self, data=None, msg=None, rejected=False, conflict_labels=None,
                 info_values=None, requirement_values=None):
        self.data = data
        self.msg = msg if msg is not None else RESP_OK
        self.rejected = rejected
        self.conflict_labels = conflict_labels or []
        self.info_values = info_values or {}
        self.requirement_values = requirement_values or {}


def decide_profile_write(existing_rows, info_values, requirement_values):
    stored = _index_rows(existing_rows)
    own_sex = _effective_own_sex(stored, info_values)
    requirement_sex = _requirement_sex_for_check(stored, requirement_values)
    if _rejects_same_sex(own_sex, requirement_sex):
        return ProfileWriteOutcome(msg=RESP_EXPECT_SAME_SEX, rejected=True)

    info_kept, conflict_keys = _split_info(stored, info_values)
    requirement_kept = _present_values(SCOPE_REQUIREMENT, requirement_values)
    labels = _labels_of(conflict_keys)
    msg = profile_conflict_msg(labels) if labels else RESP_OK
    return ProfileWriteOutcome(
        msg=msg,
        conflict_labels=labels,
        info_values=info_kept,
        requirement_values=requirement_kept,
    )


def _index_rows(existing_rows):
    return {(row.scope, row.dim_key): row for row in existing_rows or []}


def _effective_own_sex(stored, info_values):
    saved = _stated_sex_from_row(stored.get((SCOPE_INFO, "sex")))
    if saved:
        return saved
    return _stated_sex(info_values.get("sex"))


def _rejects_same_sex(own_sex, requirement_sex):
    if own_sex not in _KNOWN_SEX or requirement_sex not in _KNOWN_SEX:
        return False
    return own_sex == requirement_sex


def _split_info(stored, info_values):
    kept = {}
    conflict_keys = []
    for key in _value_keys(info_values):
        packed = info_values.get(key)
        dim = _DIM_BY_KEY.get(key)
        if dim is None or not _has_value(dim, SCOPE_INFO, packed):
            continue
        old = stored.get((SCOPE_INFO, key))
        if _same_value(dim, SCOPE_INFO, old, packed):
            continue
        if key in _LOCKED_INFO and _has_value(dim, SCOPE_INFO, _row_pack(old)):
            conflict_keys.append(key)
            continue
        kept[key] = packed
    return kept, conflict_keys


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
    if row is None:
        return None
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


def _requirement_sex_for_check(stored, requirement_values):
    """这次没提到期望性别时，用已经存下的期望来判断是不是异性。"""
    incoming = _stated_sex(requirement_values.get("sex"))
    if incoming:
        return incoming
    return _stated_sex_from_row(stored.get((SCOPE_REQUIREMENT, "sex")))


def _stated_sex(packed):
    if not packed:
        return 0
    return int(packed.get("value_min") or 0)


def _stated_sex_from_row(row):
    if row is None:
        return 0
    return int(row.value_min or 0)


def _labels_of(keys):
    key_set = set(keys)
    return [dim.label for dim in ACTIVE_DIMS if dim.key in key_set]
