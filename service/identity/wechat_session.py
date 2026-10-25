#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from service.identity.assertion import IdentityAssertion
from util.const.identity import PROVIDER_WECHAT

logger = logging.getLogger(__name__)


def parse_wechat_session(payload):
    """从 jscode2session 取出 openid。绑定了开放平台时再用 unionid 做身份密钥。"""
    if not isinstance(payload, dict):
        logger.warning("微信登录响应无效")
        return None
    errcode = payload.get('errcode')
    if errcode:
        logger.warning("微信登录失败 errcode=%s", errcode)
        return None
    openid = (payload.get('openid') or '').strip()
    unionid = (payload.get('unionid') or '').strip()
    if not openid:
        logger.warning("微信登录未返回 openid keys=%s", sorted(payload.keys()))
        return None
    if not unionid:
        logger.info("微信未返回 unionid，身份密钥使用 openid")
        unionid = openid
    return IdentityAssertion(PROVIDER_WECHAT, openid, unionid)
