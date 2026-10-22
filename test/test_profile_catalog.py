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

_LIVE_DIMS = ("sex", "birth_year", "height", "weight", "home_region")


def test_catalog_keeps_personal_dims_only():
    assert tuple(dim.key for dim in ACTIVE_DIMS) == _LIVE_DIMS
    assert FILL_REQUIRED_INFO_KEYS == ("sex", "birth_year", "height", "weight")


def test_extraction_hint_follows_catalog():
    hint = extraction_hint()
    assert "home_region" in hint
    assert "min_weight" in hint
    assert "education_level" not in hint
    assert "study_from_year" not in hint
    assert "school" not in hint


def test_payload_ignores_removed_dims_and_packs_hometown():
    info = values_from_payload(SCOPE_INFO, {
        "sex": 1,
        "home_region": "天津",
        "education_level": 4,
        "school": "某大学",
        "study_from_year": 2014,
    })
    requirement = values_from_payload(SCOPE_REQUIREMENT, {
        "home_region": "北京",
        "work": "工程师",
    })
    assert set(info) == {"sex", "home_region"}
    assert info["home_region"]["value_text"] == "天津"
    assert info["sex"]["value_min"] == 1
    assert requirement["home_region"]["value_text"] == "北京"
    assert "work" not in requirement


def test_empty_payload_packs_nothing():
    assert values_from_payload(SCOPE_INFO, None) == {}
    assert values_from_payload(SCOPE_REQUIREMENT, {}) == {}
