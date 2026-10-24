#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""见面场次的盲索引。库里能按场次找到座位，但索引本身不是场次编号。"""
import hashlib
import hmac
import logging

from util.config import get_conf

logger = logging.getLogger(__name__)

_SLOT_LABEL = b'guan-activity-slot-v1:'
_WEIXIN_SECTION = 'weixin'
_SECRET_KEY = 'secret'


def activity_slot_key(activity_id, pepper=None):
    if not activity_id:
        return ''
    secret = pepper if pepper is not None else _weixin_secret()
    if not secret:
        logger.error("无法计算见面盲索引，微信密钥为空")
        return ''
    if isinstance(secret, str):
        secret = secret.encode('utf-8')
    message = _SLOT_LABEL + str(int(activity_id)).encode('ascii')
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _weixin_secret():
    return get_conf(_SECRET_KEY, '', _WEIXIN_SECTION)
