#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from service.identity.assertion import IdentityAssertion
from util.const.identity import PROVIDER_WECHAT

logger = logging.getLogger(__name__)


def parse_wechat_session(payload):
    """从 jscode2session 取出 openid 和 unionid。session_key 不保留。"""
    if not isinstance(payload, dict):
        logger.warning("微信登录响应无效")
        return None
    errcode = payload.get('errcode')
    if errcode:
        logger.warning("微信登录失败 errcode=%s", errcode)
        return None
    openid = (payload.get('openid') or '').strip()
    unionid = (payload.get('unionid') or '').strip()
    if not openid or not unionid:
        logger.warning("微信登录未返回 openid 或 unionid")
        return None
    return IdentityAssertion(PROVIDER_WECHAT, openid, unionid)
