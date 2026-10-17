#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.common.profile_catalog import SCOPE_INFO, SCOPE_REQUIREMENT
from service.common.profile_match import inviter_passport_id, requirement_accepts, rows_to_scope_map


class _Attr(object):
    def __init__(self, scope, dim_key, value_min=0, value_max=0, value_text="", passport_id=1):
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text
        self.passport_id = passport_id


class _Activity(object):
    def __init__(self, boy_id=0, girl_id=0):
        self.boy_passport_id = boy_id
        self.girl_passport_id = girl_id


def _maps(rows):
    return rows_to_scope_map(rows, SCOPE_INFO), rows_to_scope_map(rows, SCOPE_REQUIREMENT)


def test_unset_requirement_accepts_any_info():
    info, requirement = _maps([
        _Attr(SCOPE_INFO, "sex", value_min=1),
        _Attr(SCOPE_INFO, "height", value_min=170),
    ])
    assert requirement_accepts(info, requirement) is True


def test_height_inside_range_matches():
    info, requirement = _maps([
        _Attr(SCOPE_INFO, "height", value_min=170),
        _Attr(SCOPE_REQUIREMENT, "height", value_min=160, value_max=180),
    ])
    assert requirement_accepts(info, requirement) is True


def test_height_outside_range_rejects():
    info, requirement = _maps([
        _Attr(SCOPE_INFO, "height", value_min=190),
        _Attr(SCOPE_REQUIREMENT, "height", value_min=160, value_max=175),
    ])
    assert requirement_accepts(info, requirement) is False


def test_sex_must_equal_requirement():
    info, requirement = _maps([
        _Attr(SCOPE_INFO, "sex", value_min=1),
        _Attr(SCOPE_REQUIREMENT, "sex", value_min=2),
    ])
    assert requirement_accepts(info, requirement) is False


def test_education_uses_minimum_not_exact():
    info, requirement = _maps([
        _Attr(SCOPE_INFO, "education_level", value_min=5),
        _Attr(SCOPE_REQUIREMENT, "education_level", value_min=4),
    ])
    assert requirement_accepts(info, requirement) is True


def test_education_below_minimum_rejects():
    info, requirement = _maps([
        _Attr(SCOPE_INFO, "education_level", value_min=2),
        _Attr(SCOPE_REQUIREMENT, "education_level", value_min=4),
    ])
    assert requirement_accepts(info, requirement) is False


def test_missing_info_rejects_when_requirement_is_set():
    info, requirement = _maps([
        _Attr(SCOPE_REQUIREMENT, "birth_year", value_min=1990, value_max=2000),
    ])
    assert requirement_accepts(info, requirement) is False


def test_text_requirement_blank_or_all_is_unlimited():
    info, requirement = _maps([
        _Attr(SCOPE_REQUIREMENT, "home_region", value_text="全部"),
    ])
    assert requirement_accepts(info, requirement) is True


def test_inviter_is_the_only_seated_person():
    assert inviter_passport_id(_Activity(boy_id=8)) == 8
    assert inviter_passport_id(_Activity(girl_id=9)) == 9
    assert inviter_passport_id(_Activity()) == 0
    assert inviter_passport_id(_Activity(boy_id=8, girl_id=9)) == 0
