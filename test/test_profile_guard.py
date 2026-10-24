#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.common.profile_catalog import SCOPE_INFO, SCOPE_REQUIREMENT
from service.common.profile_guard import decide_profile_write
from util.const.progress import (
    PROGRESS_AGREE,
    PROGRESS_DISAGREE,
    PROGRESS_MET,
    PROGRESS_SELECTED,
    PROGRESS_WAIT_MEET,
    voice_blocked_by_progress,
)
from util.const.response import RESP_EXPECT_SAME_SEX, RESP_PROFILE_CONFLICT_CODE


class _Attr(object):
    def __init__(self, scope, dim_key, value_min=0, value_max=0, value_text=""):
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text


def _pack(value_min=0, value_max=0, value_text=""):
    return {"value_min": value_min, "value_max": value_max, "value_text": value_text}


def test_first_voice_saves_locked_fields():
    outcome = decide_profile_write(
        [],
        {"sex": _pack(1), "height": _pack(175)},
        {"sex": _pack(2)},
    )
    assert outcome.rejected is False
    assert outcome.info_values["sex"]["value_min"] == 1
    assert outcome.info_values["height"]["value_min"] == 175
    assert outcome.requirement_values["sex"]["value_min"] == 2
    assert outcome.conflict_labels == []


def test_locked_conflict_keeps_old_and_still_saves_weight():
    existing = [
        _Attr(SCOPE_INFO, "sex", value_min=1),
        _Attr(SCOPE_INFO, "height", value_min=175),
        _Attr(SCOPE_INFO, "home_region", value_text="北京"),
    ]
    outcome = decide_profile_write(
        existing,
        {
            "sex": _pack(2),
            "height": _pack(180),
            "weight": _pack(70),
            "home_region": _pack(value_text="上海"),
        },
        {},
    )
    assert outcome.rejected is False
    assert "sex" not in outcome.info_values
    assert "height" not in outcome.info_values
    assert "home_region" not in outcome.info_values
    assert outcome.info_values["weight"]["value_min"] == 70
    assert outcome.conflict_labels == ["性别", "身高", "籍贯"]
    assert outcome.msg["code"] == RESP_PROFILE_CONFLICT_CODE


def test_same_locked_value_is_not_a_conflict():
    existing = [_Attr(SCOPE_INFO, "birth_year", value_min=1996)]
    outcome = decide_profile_write(existing, {"birth_year": _pack(1996)}, {})
    assert outcome.conflict_labels == []
    assert outcome.info_values == {}


def test_same_sex_expectation_rejects_the_whole_voice():
    outcome = decide_profile_write(
        [_Attr(SCOPE_INFO, "sex", value_min=1)],
        {"weight": _pack(70)},
        {"sex": _pack(1)},
    )
    assert outcome.rejected is True
    assert outcome.msg == RESP_EXPECT_SAME_SEX
    assert outcome.info_values == {}
    assert outcome.requirement_values == {}


def test_new_own_sex_matching_saved_requirement_is_rejected():
    outcome = decide_profile_write(
        [_Attr(SCOPE_REQUIREMENT, "sex", value_min=2)],
        {"sex": _pack(2)},
        {},
    )
    assert outcome.rejected is True


def test_opposite_requirement_is_saved():
    outcome = decide_profile_write(
        [_Attr(SCOPE_INFO, "sex", value_min=1)],
        {},
        {"sex": _pack(2)},
    )
    assert outcome.rejected is False
    assert outcome.requirement_values["sex"]["value_min"] == 2


def test_voice_blocked_only_for_double_half_and_solid():
    assert voice_blocked_by_progress(PROGRESS_WAIT_MEET) is True
    assert voice_blocked_by_progress(PROGRESS_MET) is True
    assert voice_blocked_by_progress(PROGRESS_AGREE) is True
    assert voice_blocked_by_progress(PROGRESS_DISAGREE) is False
    assert voice_blocked_by_progress(PROGRESS_SELECTED) is False
