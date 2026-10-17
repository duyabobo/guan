#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""把维度目录和已存的值收成小程序直接渲染的行。不访问数据库。"""
import re

from service.common.profile_catalog import (
    ACTIVE_DIMS,
    KIND_CHOICE,
    KIND_NUMBER,
    KIND_RANGE,
    KIND_TEXT,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
)

MISSING_MARK = "—"
_ALL_WORD = "全部"
_REGION_DUP = re.compile(r"(北京市|天津市|上海市|重庆市)\1")


def build_rows(attr_rows):
    """只读 profile_attr。没有对应行的维度不展示。"""
    attr_index = {(row.scope, row.dim_key): row for row in attr_rows or []}
    rows = []
    for dim in ACTIVE_DIMS:
        info_value = _side_value(dim, SCOPE_INFO, attr_index)
        requirement_value = _side_value(dim, SCOPE_REQUIREMENT, attr_index)
        if not info_value and not requirement_value:
            continue
        rows.append({
            "dimKey": dim.key,
            "label": dim.label,
            "infoValue": info_value or MISSING_MARK,
            "requirementValue": requirement_value or MISSING_MARK,
            "infoMissing": not info_value,
            "requirementMissing": not requirement_value,
        })
    return rows


def display_from_attr(dim, row):
    kind = dim.kind_of(row.scope)
    if kind == KIND_TEXT:
        return _present_text(row.value_text)
    if kind == KIND_CHOICE:
        return _choice_text(dim.choices, row.value_min)
    if kind == KIND_RANGE:
        return format_range(row.value_min, row.value_max, dim.unit)
    if kind == KIND_NUMBER:
        return _number_text(row.value_min, dim.unit)
    return ""


def format_range(value_min, value_max, unit):
    if not value_min and not value_max:
        return ""
    if value_min and value_max:
        text = "%s-%s" % (value_min, value_max)
    else:
        text = str(value_min or value_max)
    if unit:
        text += unit
    return text


def _side_value(dim, scope, attr_index):
    stored = attr_index.get((scope, dim.key))
    if stored is None:
        return ""
    return display_from_attr(dim, stored)


def _choice_text(choices, index):
    index = index or 0
    if index <= 0 or index >= len(choices):
        return ""
    return choices[index]


def _number_text(value, unit):
    if not value:
        return ""
    text = str(value)
    if unit:
        text += unit
    return text


def _present_text(text):
    tightened = _REGION_DUP.sub(r"\1", str(text or ""))
    if not tightened or tightened.replace(_ALL_WORD, "").strip() == "":
        return ""
    return tightened
