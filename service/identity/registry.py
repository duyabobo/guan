#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from util.const.identity import PROVIDER_NATIONAL_NETWORK, PROVIDER_WECHAT

logger = logging.getLogger(__name__)


def get_provider(provider_code):
    if provider_code == PROVIDER_WECHAT:
        from service.identity.wechat import WechatIdentityProvider
        return WechatIdentityProvider()
    if provider_code == PROVIDER_NATIONAL_NETWORK:
        from service.identity.national_network import NationalNetworkIdentityProvider
        return NationalNetworkIdentityProvider()
    logger.warning("未知身份提供方 %s", provider_code)
    return None
