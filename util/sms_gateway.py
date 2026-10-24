#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""短信出口。地址来自 sms.sms_url。日志不记号码和正文。"""
import json
import logging
from urllib import request as urlrequest

from util.config import get_conf
from util.const.notice import WX_HTTP_TIMEOUT_SEC
from util.wx_http import path_of

logger = logging.getLogger(__name__)

SMS_SECTION = 'sms'
SMS_URL_KEY = 'sms_url'
SMS_TOKEN_KEY = 'sms_token'
SMS_TOKEN_HEADER = 'X-Sms-Token'


def sms_configured():
    return bool(get_conf(SMS_URL_KEY, '', SMS_SECTION))


def post_messages(messages):
    url = get_conf(SMS_URL_KEY, '', SMS_SECTION)
    if not url or not messages:
        return False
    token = get_conf(SMS_TOKEN_KEY, '', SMS_SECTION)
    logger.info("请求短信 path=%s count=%s", path_of(url), len(messages))
    headers = {'Content-Type': 'application/json'}
    if token:
        headers[SMS_TOKEN_HEADER] = token
    body = json.dumps({'messages': messages}, ensure_ascii=False).encode('utf-8')
    req = urlrequest.Request(url, data=body, headers=headers)
    try:
        with urlrequest.urlopen(req, timeout=WX_HTTP_TIMEOUT_SEC) as resp:
            return 200 <= resp.status < 300
    except Exception:
        logger.exception("短信发送失败")
        return False
