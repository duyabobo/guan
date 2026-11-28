#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.common.page_copy import guan_info_copy, list_page_copy, match_config_copy
from service.common.profile_catalog import SCOPE_INFO
from service.common.profile_rows import build_rows
from service.common.review_mode import phone_required
from service.phone_bind import PhoneBindService
from util.const.response import RESP_PHONE_REQUIRED


class _Attr(object):
    def __init__(self, scope, dim_key, value_min=0, value_max=0, value_text=""):
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text


def test_phone_required_when_review_off(monkeypatch):
    monkeypatch.delenv("UNDER_REVIEW", raising=False)
    assert phone_required() is True
    assert PhoneBindService().block_if_unbound(0)["code"] == RESP_PHONE_REQUIRED["code"]


def test_phone_not_required_when_review_on(monkeypatch):
    monkeypatch.setenv("UNDER_REVIEW", "1")
    assert phone_required() is False
    assert PhoneBindService().block_if_unbound(0) is None


def test_review_on_does_not_change_copy_or_labels(monkeypatch):
    """审核只关手机号校验，文案和维度标签与正常一致。"""
    monkeypatch.setenv("UNDER_REVIEW", "1")
    assert list_page_copy()["entryTitle"] == "关关雎鸠"
    assert list_page_copy()["showHeart"] is True
    assert guan_info_copy()["pageTitle"] == "活动详情"
    detail = match_config_copy()
    assert detail["infoTitle"] == "我的信息"
    assert detail["requirementTitle"] == "我的期望"
    assert detail["voiceStatus"]["idle"] == "勇敢发声"
    assert "手机号" in detail["privacyBody"]
    rows = build_rows([
        _Attr(SCOPE_INFO, "height", value_min=170),
        _Attr(SCOPE_INFO, "home_region", value_text="北京"),
    ])
    by_key = {row["dimKey"]: row for row in rows}
    assert by_key["height"]["label"] == "身高"
    assert by_key["height"]["infoValue"] == "170cm"
    assert by_key["home_region"]["label"] == "籍贯"
