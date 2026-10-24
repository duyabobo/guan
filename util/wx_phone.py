#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""用手机号按钮返回的 code 向微信换号码。日志不记号码。"""
import logging

from util.const.notice import WX_HTTP_TIMEOUT_SEC
from util.wx_http import post_json
from util.wx_subscribe import access_token

logger = logging.getLogger(__name__)

_PHONE_URL = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber'


def phone_info(code):
    token = access_token()
    if not token or not code:
        logger.info("换取手机号缺少 token 或 code")
        return {}
    url = '%s?access_token=%s' % (_PHONE_URL, token)
    try:
        payload = post_json(url, {'code': code}, WX_HTTP_TIMEOUT_SEC)
    except Exception:
        logger.exception("换取手机号失败")
        return {}
    errcode = payload.get('errcode')
    if errcode:
        logger.info("换取手机号被微信拒绝 errcode=%s", errcode)
        return {}
    info = payload.get('phone_info') or {}
    if not isinstance(info, dict):
        return {}
    return info
