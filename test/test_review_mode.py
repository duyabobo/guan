#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.common.page_copy import guan_info_copy, list_page_copy, match_config_copy
from service.common.profile_catalog import (
    DRINK_CHOICES,
    HOUSE_CHOICES,
    MARRIAGE_CHOICES,
    SCOPE_INFO,
    SCOPE_REQUIREMENT,
    SMOKE_CHOICES,
)
from service.common.profile_guard import decide_profile_write
from service.common.profile_rows import build_rows
from service.common.review_mode import (
    phone_required,
    present_buttons,
    present_client_msg,
    present_progress_desc,
    present_sentence,
)
from service.phone_bind import PhoneBindService
from service.match_config import MatchConfigService
from util.const.base import (
    GUAN_INFO_OP_TYPE_INVITE,
    GUAN_INFO_OP_TYPE_JOIN,
    GUAN_INFO_OP_TYPE_QUIT,
    MODEL_MEET_RESULT_FIT_CHOICE,
    MODEL_MEET_RESULT_UNKNOWN,
)
from util.const import response as response_module
from util.const.progress import (
    HALF_FIT_HINT,
    PROGRESS_AGREE,
    PROGRESS_DESC,
    PROGRESS_DISAGREE,
    PROGRESS_MET,
    PROGRESS_NOT_SELECTED,
    PROGRESS_SELECTED,
    PROGRESS_WAIT_MEET,
    get_bottom_buttons,
)
from util.const.response import (
    RESP_EXPECT_SAME_SEX,
    RESP_OK,
    RESP_PHONE_REQUIRED,
    RESP_SIGN_INVALID,
)

_BANNED = (
    "见面", "婚", "恋", "相亲", "对象", "异性", "合适", "期望",
    "征婚", "脱单", "交友", "实心", "购房", "婚姻", "籍贯", "收入",
    "吸烟", "喝酒", "未婚", "离异", "丧偶", "匹配", "想找", "雎鸠",
    "在一起", "ta的",
)

_BUTTON_CASES = (
    (PROGRESS_NOT_SELECTED, GUAN_INFO_OP_TYPE_INVITE, False, MODEL_MEET_RESULT_UNKNOWN),
    (PROGRESS_NOT_SELECTED, GUAN_INFO_OP_TYPE_JOIN, False, MODEL_MEET_RESULT_UNKNOWN),
    (PROGRESS_SELECTED, GUAN_INFO_OP_TYPE_QUIT, False, MODEL_MEET_RESULT_UNKNOWN),
    (PROGRESS_WAIT_MEET, GUAN_INFO_OP_TYPE_QUIT, False, MODEL_MEET_RESULT_UNKNOWN),
    (PROGRESS_WAIT_MEET, GUAN_INFO_OP_TYPE_QUIT, True, MODEL_MEET_RESULT_UNKNOWN),
    (PROGRESS_MET, GUAN_INFO_OP_TYPE_QUIT, True, MODEL_MEET_RESULT_UNKNOWN),
    (PROGRESS_MET, GUAN_INFO_OP_TYPE_QUIT, True, MODEL_MEET_RESULT_FIT_CHOICE),
    (PROGRESS_AGREE, GUAN_INFO_OP_TYPE_QUIT, True, MODEL_MEET_RESULT_UNKNOWN),
    (PROGRESS_DISAGREE, GUAN_INFO_OP_TYPE_QUIT, True, MODEL_MEET_RESULT_UNKNOWN),
)


class _Attr(object):
    def __init__(self, scope, dim_key, value_min=0, value_max=0, value_text=""):
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text


def _pack(value_min=0, value_text=""):
    return {"value_min": value_min, "value_max": 0, "value_text": value_text}


def _texts(value):
    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for item in value.values():
            for text in _texts(item):
                yield text
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            for text in _texts(item):
                yield text


def _banned_in(value):
    hits = []
    for text in _texts(value):
        for word in _BANNED:
            if word in text:
                hits.append("%s <= %s" % (word, text))
    return hits


def _review_on(monkeypatch):
    monkeypatch.setenv("UNDER_REVIEW", "1")


def test_default_copy_stays_dating_words(monkeypatch):
    monkeypatch.delenv("UNDER_REVIEW", raising=False)
    assert list_page_copy()["listTitle"] == "见面"
    assert list_page_copy()["entryTitle"] == "关关雎鸠"
    assert list_page_copy()["showHeart"] is True
    assert guan_info_copy()["pageTitle"] == "见面详情"
    detail = match_config_copy()
    assert detail["infoTitle"] == "我的信息"
    assert detail["requirementTitle"] == "我的期望"
    assert "见面" in detail["privacyBody"]
    assert present_client_msg(RESP_EXPECT_SAME_SEX) is RESP_EXPECT_SAME_SEX
    kept = present_buttons([{"label": "发起见面", "hint": HALF_FIT_HINT}])
    assert kept[0]["label"] == "发起见面"
    assert kept[0]["hint"] == HALF_FIT_HINT
    assert phone_required() is True
    assert PhoneBindService().block_if_unbound(0)["code"] == RESP_PHONE_REQUIRED["code"]


def test_default_rows_keep_catalog_words():
    rows = build_rows([
        _Attr(SCOPE_INFO, "height", value_min=170),
        _Attr(SCOPE_INFO, "marriage", value_min=MARRIAGE_CHOICES.index("未婚")),
        _Attr(SCOPE_INFO, "income", value_min=8000),
    ])
    by_key = {row["dimKey"]: row for row in rows}
    assert by_key["height"]["label"] == "身高"
    assert by_key["height"]["infoValue"] == "170cm"
    assert by_key["marriage"]["label"] == "婚姻"
    assert by_key["marriage"]["infoValue"] == "未婚"
    assert by_key["income"]["infoValue"] == "8000元/月"


def test_review_pages_use_activity_words(monkeypatch):
    _review_on(monkeypatch)
    listing = list_page_copy()
    detail = guan_info_copy()
    profile = match_config_copy()
    assert listing["listTitle"] == "活动"
    assert listing["entryTitle"] == ""
    assert listing["showHeart"] is False
    assert detail["pageTitle"] == "活动详情"
    assert profile["infoTitle"] == "报名信息"
    assert profile["requirementTitle"] == "参与偏好"
    assert profile["pageTitle"] == "活动报名"
    assert profile["voiceStatus"]["idle"] == "说说你自己和想参加的活动"
    assert _banned_in(listing) == []
    assert _banned_in(detail) == []
    assert _banned_in(profile) == []


def test_review_rows_relabel_dating_dims(monkeypatch):
    _review_on(monkeypatch)
    rows = build_rows([
        _Attr(SCOPE_INFO, "sex", value_min=1),
        _Attr(SCOPE_INFO, "height", value_min=170),
        _Attr(SCOPE_INFO, "income", value_min=8000),
        _Attr(SCOPE_INFO, "marriage", value_min=MARRIAGE_CHOICES.index("未婚")),
        _Attr(SCOPE_REQUIREMENT, "marriage", value_min=MARRIAGE_CHOICES.index("离异")),
        _Attr(SCOPE_INFO, "has_house", value_min=HOUSE_CHOICES.index("已购房")),
        _Attr(SCOPE_INFO, "smoking", value_min=SMOKE_CHOICES.index("经常吸烟")),
        _Attr(SCOPE_INFO, "drinking", value_min=DRINK_CHOICES.index("不喝酒")),
    ], show_all=True)
    by_key = {row["dimKey"]: row for row in rows}
    assert by_key["sex"]["label"] == "性别"
    assert by_key["sex"]["infoValue"] == "男"
    assert by_key["height"]["label"] == "身高"
    assert by_key["height"]["infoValue"] == "170cm"
    assert by_key["income"]["label"] == "预算"
    assert by_key["income"]["infoValue"] == "8000元"
    assert by_key["marriage"]["label"] == "参加经验"
    assert by_key["marriage"]["infoValue"] == "第一次"
    assert by_key["marriage"]["requirementValue"] == "参加过"
    assert by_key["has_house"]["infoValue"] == "自驾"
    assert by_key["smoking"]["infoValue"] == "需注意"
    assert by_key["drinking"]["infoValue"] == "无忌口"
    blank = build_rows([_Attr(SCOPE_INFO, "marriage", value_min=0)])
    assert blank == []
    assert _banned_in(rows) == []


def test_review_choice_last_index_stays_visible(monkeypatch):
    _review_on(monkeypatch)
    catalogs = (
        ("marriage", MARRIAGE_CHOICES),
        ("has_house", HOUSE_CHOICES),
        ("smoking", SMOKE_CHOICES),
        ("drinking", DRINK_CHOICES),
    )
    for key, catalog in catalogs:
        rows = build_rows([_Attr(SCOPE_INFO, key, value_min=len(catalog) - 1)])
        assert rows[0]["infoValue"]
        assert rows[0]["infoValue"] != catalog[-1]


def test_review_buttons_progress_and_errors(monkeypatch):
    _review_on(monkeypatch)
    invite = get_bottom_buttons(
        PROGRESS_NOT_SELECTED, GUAN_INFO_OP_TYPE_INVITE, False, MODEL_MEET_RESULT_UNKNOWN,
    )
    shown = present_buttons(invite)
    assert invite[0]["label"] == "发起见面"
    assert [item["label"] for item in shown] == ["参加"]
    assert shown[0]["opType"] == invite[0]["opType"]
    assert shown[0]["action"] == invite[0]["action"]
    for status, op_type, ready, result in _BUTTON_CASES:
        buttons = get_bottom_buttons(status, op_type, ready, result)
        shown_buttons = present_buttons(buttons)
        assert _banned_in(shown_buttons) == []
        labels = [item["label"] for item in shown_buttons]
        if status == PROGRESS_NOT_SELECTED:
            assert labels == ["参加"]
            assert shown_buttons[0]["opType"] == buttons[0]["opType"]
        else:
            assert labels == []
    for text in PROGRESS_DESC.values():
        assert _banned_in(present_progress_desc(text)) == []
    assert present_progress_desc("待见面") == "待参加"
    assert present_progress_desc("在一起") == "已确认"
    assert present_progress_desc("") == ""
    assert present_buttons(None) == []
    assert present_sentence("") == ""
    shown_msg = present_client_msg(RESP_EXPECT_SAME_SEX)
    assert shown_msg is not RESP_EXPECT_SAME_SEX
    assert shown_msg["code"] == RESP_EXPECT_SAME_SEX["code"]
    assert RESP_EXPECT_SAME_SEX["errMsg"] == "目前只支持异性期望，请改成异性后再试"
    assert _banned_in(shown_msg["errMsg"]) == []
    assert present_client_msg(RESP_OK) is RESP_OK
    assert present_client_msg(None) is None
    assert present_client_msg(RESP_SIGN_INVALID) is RESP_SIGN_INVALID
    assert phone_required() is False
    assert PhoneBindService().block_if_unbound(0) is None


def test_every_dating_error_has_review_sentence(monkeypatch):
    _review_on(monkeypatch)
    covered = False
    for value in vars(response_module).values():
        if not isinstance(value, dict):
            continue
        err = value.get("errMsg")
        if not err or not _banned_in(err):
            continue
        covered = True
        shown = present_sentence(err)
        assert shown != err
        assert _banned_in(shown) == []
    assert covered is True


def test_review_conflict_label_uses_activity_name(monkeypatch):
    _review_on(monkeypatch)
    outcome = decide_profile_write(
        [_Attr(SCOPE_INFO, "home_region", value_text="北京")],
        {"home_region": _pack(value_text="上海")},
        {},
    )
    assert outcome.conflict_labels == ["所在地区"]
    assert _banned_in(outcome.msg["errMsg"]) == []


def test_voice_block_text_follows_review_switch(monkeypatch):
    _review_on(monkeypatch)
    monkeypatch.setattr("service.match_config.voice_entry_blocked", lambda passport_id: True)
    monkeypatch.setattr(
        "service.match_config.ProfileBoardService.rows_for",
        lambda passport_id, show_all=False: [],
    )
    monkeypatch.setattr("service.match_config.PhoneBindService.bound", lambda self, passport_id: True)
    data = MatchConfigService({"id": 1}).getMatchConfig()
    assert data["voiceBlockText"] == "已经报名或确认参加，暂时不能再修改"
    assert data["copy"]["privacyBody"].startswith("点按麦克风后")
    assert _banned_in(data["voiceBlockText"]) == []
