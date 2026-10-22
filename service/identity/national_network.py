#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from tornado import gen

from util.const.identity import PROVIDER_NATIONAL_NETWORK

logger = logging.getLogger(__name__)


class NationalNetworkIdentityProvider(object):
    """国家网络身份认证。接入时实现 authenticate，登录和加密不用改调用方。"""

    code = PROVIDER_NATIONAL_NETWORK

    @gen.coroutine
    def authenticate(self, credential):
        logger.error("国家网络身份认证尚未接入")
        raise gen.Return(None)
