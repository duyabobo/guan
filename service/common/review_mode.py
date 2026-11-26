#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""审核开关。为 1 时不校验手机号绑定，其余行为与正常一致。"""
import logging

from util.config import get_conf

logger = logging.getLogger(__name__)

REVIEW_SECTION = "global"
REVIEW_KEY = "under_review"
REVIEW_OFF = "0"
REVIEW_ON = "1"

_announced = False


def under_review():
    enabled = get_conf(REVIEW_KEY, REVIEW_OFF, REVIEW_SECTION).strip() == REVIEW_ON
    global _announced
    if enabled and not _announced:
        logger.info("审核开关为 1，不校验手机号绑定")
        _announced = True
    return enabled


def phone_required():
    """审核时不拦手机号。调用方把这个结果放进接口，页面按它决定要不要验证。"""
    return not under_review()
