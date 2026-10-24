#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.common.profile_catalog import (
    ACTIVE_DIMS,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
    values_from_payload,
)
from service.common.profile_rows import MISSING_MARK, build_rows, missing_required_info_keys
class _Attr(object):
    def __init__(self, scope, dim_key, value_min=0, value_max=0, value_text=""):
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text


def test_dim_keys_unique():
    keys = [dim.key for dim in ACTIVE_DIMS]
    assert len(keys) == len(set(keys))


def test_rows_use_catalog_label_and_unit():
    rows = build_rows([
        _Attr(SCOPE_INFO, "height", value_min=170),
        _Attr(SCOPE_REQUIREMENT, "height", value_min=160, value_max=180),
    ])
    height = next(row for row in rows if row["dimKey"] == "height")
    assert height["label"] == "身高"
    assert height["infoValue"] == "170cm"
    assert height["requirementValue"] == "160-180cm"
    assert height["infoMissing"] is False
    assert height["requirementMissing"] is False
    assert height["required"] is True


def test_missing_side_uses_mark_and_blank_dim_is_omitted():
    rows = build_rows([
        _Attr(SCOPE_INFO, "birth_year", value_min=1995),
    ])
    assert [row["dimKey"] for row in rows] == ["birth_year"]
    assert rows[0]["requirementValue"] == MISSING_MARK
    assert rows[0]["requirementMissing"] is True


def test_choice_index_zero_is_blank():
    rows = build_rows([_Attr(SCOPE_INFO, "sex", value_min=0)])
    assert rows == []


def test_required_info_includes_weight_and_hometown():
    filled = {
        "sex": _Attr(SCOPE_INFO, "sex", value_min=1),
        "birth_year": _Attr(SCOPE_INFO, "birth_year", value_min=1996),
        "height": _Attr(SCOPE_INFO, "height", value_min=175),
        "weight": _Attr(SCOPE_INFO, "weight", value_min=65),
        "home_region": _Attr(SCOPE_INFO, "home_region", value_text="北京"),
    }
    assert missing_required_info_keys(filled) == []
    without_weight = dict(filled)
    without_weight.pop("weight")
    assert missing_required_info_keys(without_weight) == ["weight"]
    without_hometown = dict(filled)
    without_hometown.pop("home_region")
    assert missing_required_info_keys(without_hometown) == ["home_region"]


def test_show_all_keeps_unmentioned_dims_empty():
    rows = build_rows([
        _Attr(SCOPE_INFO, "sex", value_min=1),
    ], show_all=True)
    assert [row["dimKey"] for row in rows] == [dim.key for dim in ACTIVE_DIMS]
    sex = rows[0]
    assert sex["infoValue"] == "男"
    assert sex["requirementValue"] == MISSING_MARK
    assert sex["requirementMissing"] is True
    height = next(row for row in rows if row["dimKey"] == "height")
    weight = next(row for row in rows if row["dimKey"] == "weight")
    assert height["infoValue"] == MISSING_MARK
    assert height["requirementValue"] == MISSING_MARK
    assert height["required"] is True
    assert weight["required"] is True
    hobby = next(row for row in rows if row["dimKey"] == "hobby")
    assert hobby["required"] is False
    assert hobby["infoValue"] == MISSING_MARK


def test_values_from_payload_packs_single_and_range():
    info = values_from_payload(SCOPE_INFO, {"height": 170, "sex": 1, "unknown": 1})
    requirement = values_from_payload(SCOPE_REQUIREMENT, {"min_height": 160, "max_height": 175})
    assert info["height"]["value_min"] == 170
    assert info["sex"]["value_min"] == 1
    assert "unknown" not in info
    assert requirement["height"]["value_min"] == 160
    assert requirement["height"]["value_max"] == 175
    assert "sex" not in requirement


def test_duplicate_city_prefix_is_collapsed():
    rows = build_rows([
        _Attr(SCOPE_INFO, "home_region", value_text="北京市北京市海淀区"),
        _Attr(SCOPE_REQUIREMENT, "home_region", value_text="全部"),
    ])
    assert len(rows) == 1
    assert rows[0]["infoValue"] == "北京市海淀区"
    assert rows[0]["requirementValue"] == MISSING_MARK
    assert rows[0]["requirementMissing"] is True
