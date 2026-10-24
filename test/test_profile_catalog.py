#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.common.profile_catalog import (
    ACTIVE_DIMS,
    FILL_REQUIRED_INFO_KEYS,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
    extraction_hint,
    values_from_payload,
)

_LIVE_DIMS = (
    "sex", "birth_year", "height", "weight", "home_region", "live_region",
    "job", "income", "school", "first_degree", "major", "has_house", "house_region",
    "marriage", "smoking", "drinking", "hobby",
)


def test_catalog_keeps_personal_dims_only():
    assert tuple(dim.key for dim in ACTIVE_DIMS) == _LIVE_DIMS
    assert FILL_REQUIRED_INFO_KEYS == ("sex", "birth_year", "height", "weight", "home_region")


def test_extraction_hint_follows_catalog():
    hint = extraction_hint()
    assert "home_region" in hint
    assert "live_region" in hint
    assert "min_weight" in hint
    assert "未婚" in hint
    assert "school" in hint
    assert "first_degree" in hint
    assert "本科" in hint
    assert "education_level" not in hint
    assert "study_from_year" not in hint


def test_payload_packs_school_and_ignores_unknown_fields():
    info = values_from_payload(SCOPE_INFO, {
        "sex": 1,
        "home_region": "天津",
        "school": "某大学",
        "education_level": 4,
        "study_from_year": 2014,
    })
    requirement = values_from_payload(SCOPE_REQUIREMENT, {
        "home_region": "北京",
        "job": "工程师",
        "work": "旧职业字段",
    })
    assert info["school"]["value_text"] == "某大学"
    assert info["home_region"]["value_text"] == "天津"
    assert "education_level" not in info
    assert "study_from_year" not in info
    assert requirement["job"]["value_text"] == "工程师"
    assert "work" not in requirement


def test_choice_label_packs_to_catalog_index():
    info = values_from_payload(SCOPE_INFO, {
        "marriage": "未婚",
        "smoking": "经常吸烟",
        "first_degree": "本科",
        "has_house": "已购房",
    })
    assert info["marriage"]["value_min"] == 1
    assert info["smoking"]["value_min"] == 3
    assert info["first_degree"]["value_min"] == 3
    assert info["has_house"]["value_min"] == 2
    assert values_from_payload(SCOPE_INFO, {"marriage": "没听清"}) == {}


def test_empty_payload_packs_nothing():
    assert values_from_payload(SCOPE_INFO, None) == {}
    assert values_from_payload(SCOPE_REQUIREMENT, {}) == {}
