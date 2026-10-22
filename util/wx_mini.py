#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from tornado import gen

import util.config
from util.async_request import asyncRequest
from util.const.mini_program import WX_MINIPROGRAM_CODE_TO_SESSION

logger = logging.getLogger(__name__)

CODE_TO_SESSION_TIMEOUT = 3


class WxHelper(object):
    def __init__(self):
        self.appid = util.config.get("weixin", "appid")
        self.secret = util.config.get("weixin", "secret")

    @gen.coroutine
    def codeToSession(self, js_code):
        """向微信换登录态。quiet 避免把 code、secret、unionid 打进日志。"""
        if not js_code:
            logger.warning("微信 code 为空")
            raise gen.Return({})
        payload = yield asyncRequest(
            WX_MINIPROGRAM_CODE_TO_SESSION,
            {
                'js_code': js_code,
                'appid': self.appid,
                'secret': self.secret,
                'grant_type': 'authorization_code',
            },
            timeout=CODE_TO_SESSION_TIMEOUT,
            quiet=True,
        )
        raise gen.Return(payload or {})
