#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""审核开关。为 1 时，对外文案改成线下活动报名，详情只保留参加，并且不校验手机号。

列表不按距离筛选，未开始的活动都返回。

资料维度和选项下标仍用原来的目录，只换展示。
"""
import logging

from util.config import get_conf
from util.const.base import GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN
from util.const.response import (
    RESP_EXPECT_SAME_SEX,
    RESP_HAS_APPOINTMENT,
    RESP_HAS_FIT_PARTNER,
    RESP_HAS_TIME_CONFLICT,
    RESP_JOIN_ACTIVITY_FAILED,
    RESP_MEET_RESULT_ERR,
    RESP_NEED_FILL_INFO,
    RESP_VOICE_IN_PROGRESS,
)

logger = logging.getLogger(__name__)

REVIEW_SECTION = "global"
REVIEW_KEY = "under_review"
REVIEW_OFF = "0"
REVIEW_ON = "1"

_announced = False

# 选项下标必须和目录一致，只换展示文字。
_REVIEW_CHOICES = {
    "marriage": ["未知", "第一次", "参加过", "暂不参加"],
    "has_house": ["未知", "公共交通", "自驾"],
    "smoking": ["未知", "良好", "一般", "需注意"],
    "drinking": ["未知", "无忌口", "少油少辣", "有忌口"],
}

_REVIEW_DIM_LABEL = {
    "home_region": "所在地区",
    "live_region": "常住城市",
    "income": "预算",
    "school": "学校",
    "first_degree": "学历",
    "has_house": "交通",
    "house_region": "集合地点",
    "marriage": "参加经验",
    "smoking": "身体状况",
    "drinking": "饮食",
}

_REVIEW_DIM_UNIT = {
    "income": "元",
}

REVIEW_JOIN_LABEL = "参加"
_JOIN_OP_TYPES = frozenset({GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN})

_REVIEW_PROGRESS = {
    "待配置": "待填写",
    "待见面": "待参加",
    "在一起": "已确认",
    "不合适": "不参加",
}

_REVIEW_SENTENCE = {
    RESP_NEED_FILL_INFO["errMsg"]: "请完善报名信息",
    RESP_VOICE_IN_PROGRESS["errMsg"]: "已经报名或确认参加，暂时不能再修改",
    RESP_EXPECT_SAME_SEX["errMsg"]: "报名条件不符合，请调整后再试",
    RESP_JOIN_ACTIVITY_FAILED["errMsg"]: "本次活动名额已满，请返回重新选择",
    RESP_HAS_APPOINTMENT["errMsg"]: "已经报名了一场活动，不能再报别的",
    RESP_HAS_FIT_PARTNER["errMsg"]: "已经有进行中的活动，不能再报名",
    RESP_HAS_TIME_CONFLICT["errMsg"]: "您有其他活动和本次时间冲突，请返回重新选择",
    RESP_MEET_RESULT_ERR["errMsg"]: "修改参加结果失败",
}


def under_review():
    enabled = get_conf(REVIEW_KEY, REVIEW_OFF, REVIEW_SECTION).strip() == REVIEW_ON
    global _announced
    if enabled and not _announced:
        logger.info("审核开关为 1，文案按活动报名返回，详情只保留参加，不校验手机号，列表不按距离筛选")
        _announced = True
    return enabled


def client_label(dim):
    if under_review():
        return _REVIEW_DIM_LABEL.get(dim.key, dim.label)
    return dim.label


def client_unit(dim):
    if under_review() and dim.key in _REVIEW_DIM_UNIT:
        return _REVIEW_DIM_UNIT[dim.key]
    return dim.unit


def client_choices(dim):
    if under_review() and dim.key in _REVIEW_CHOICES:
        return _REVIEW_CHOICES[dim.key]
    return dim.choices


def present_sentence(text):
    if not text or not under_review():
        return text
    return _REVIEW_SENTENCE.get(text, text)


def present_client_msg(msg):
    """给小程序的 errMsg。不改原字典，业务判断仍用原来的 code。"""
    if not msg:
        return msg
    err = msg.get("errMsg")
    shown = present_sentence(err) if err else err
    if shown == err:
        return msg
    copied = dict(msg)
    copied["errMsg"] = shown
    return copied


def present_progress_desc(text):
    if not text or not under_review():
        return text
    return _REVIEW_PROGRESS.get(text, text)


def phone_required():
    """审核时不拦手机号。调用方把这个结果放进接口，页面按它决定要不要验证。"""
    return not under_review()


def present_buttons(buttons):
    """审核时底部只保留发起或加入，文案统一成参加。取消、合适这些按钮不出现。"""
    if not under_review():
        return buttons or []
    join = _review_join_button(buttons)
    if join is None:
        return []
    return [join]


def _review_join_button(buttons):
    for button in buttons or []:
        if button.get("action") != "operate" or button.get("opType") not in _JOIN_OP_TYPES:
            continue
        item = dict(button)
        item["label"] = REVIEW_JOIN_LABEL
        return item
    return None
