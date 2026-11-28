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
from util.const.response import RESP_EXPECT_SAME_SEX


class _Attr(object):
    def __init__(self, scope, dim_key, value_min=0, value_max=0, value_text=""):
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text


def _pack(value_min=0, value_max=0, value_text=""):
    return {"value_min": value_min, "value_max": value_max, "value_text": value_text}


def test_first_voice_saves_info_fields():
    outcome = decide_profile_write(
        [],
        {"sex": _pack(1), "height": _pack(175)},
        {"sex": _pack(2)},
    )
    assert outcome.rejected is False
    assert outcome.info_values["sex"]["value_min"] == 1
    assert outcome.info_values["height"]["value_min"] == 175
    assert outcome.requirement_values["sex"]["value_min"] == 2


def test_info_fields_can_be_overwritten():
    existing = [
        _Attr(SCOPE_INFO, "sex", value_min=1),
        _Attr(SCOPE_INFO, "height", value_min=175),
        _Attr(SCOPE_INFO, "birth_year", value_min=1996),
        _Attr(SCOPE_INFO, "home_region", value_text="北京"),
    ]
    outcome = decide_profile_write(
        existing,
        {
            "sex": _pack(2),
            "height": _pack(180),
            "birth_year": _pack(1998),
            "weight": _pack(70),
            "home_region": _pack(value_text="上海"),
        },
        {"sex": _pack(1)},
    )
    assert outcome.rejected is False
    assert outcome.info_values["sex"]["value_min"] == 2
    assert outcome.info_values["height"]["value_min"] == 180
    assert outcome.info_values["birth_year"]["value_min"] == 1998
    assert outcome.info_values["weight"]["value_min"] == 70
    assert outcome.info_values["home_region"]["value_text"] == "上海"
    assert outcome.requirement_values["sex"]["value_min"] == 1


def test_same_info_value_is_not_rewritten():
    existing = [_Attr(SCOPE_INFO, "birth_year", value_min=1996)]
    outcome = decide_profile_write(existing, {"birth_year": _pack(1996)}, {})
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


def test_changing_own_sex_with_matching_new_requirement_is_allowed():
    existing = [
        _Attr(SCOPE_INFO, "sex", value_min=1),
        _Attr(SCOPE_REQUIREMENT, "sex", value_min=2),
    ]
    outcome = decide_profile_write(
        existing,
        {"sex": _pack(2)},
        {"sex": _pack(1)},
    )
    assert outcome.rejected is False
    assert outcome.info_values["sex"]["value_min"] == 2
    assert outcome.requirement_values["sex"]["value_min"] == 1


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
