#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from tornado import gen

from service.identity.wechat_session import parse_wechat_session
from util.const.identity import PROVIDER_WECHAT
from util.wx_mini import WxHelper

logger = logging.getLogger(__name__)


class WechatIdentityProvider(object):
    code = PROVIDER_WECHAT

    @gen.coroutine
    def authenticate(self, credential):
        if not credential:
            logger.warning("微信登录缺少 code")
            raise gen.Return(None)
        payload = yield WxHelper().codeToSession(credential)
        raise gen.Return(parse_wechat_session(payload))
