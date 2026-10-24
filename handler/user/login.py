#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import logging

from tornado import gen

from handler.basehandler import BaseHandler
from ral.passport import delSession
from service.identity.registry import get_provider
from service.login import LoginService
from util.const.identity import PROVIDER_WECHAT
from util.const.response import RESP_IDENTITY_INCOMPLETE, RESP_NEED_LOGIN
from util.monitor import superMonitor, Response, superGenMonitor

logger = logging.getLogger(__name__)


class LoginHandler(BaseHandler):
    __model__ = ''

    @superGenMonitor
    @gen.coroutine
    def get(self, *args, **kwargs):
        """只接受微信登录。身份以微信 jscode2session 的返回为准，不采信调用方自称的身份。"""
        asked = self.getRequestParameter('provider', PROVIDER_WECHAT)
        if asked != PROVIDER_WECHAT:
            logger.warning("拒绝非微信登录 provider=%s", asked)
        provider = get_provider(PROVIDER_WECHAT)
        if not provider:
            raise gen.Return(Response(msg=RESP_NEED_LOGIN))

        assertion = yield provider.authenticate(self.getRequestParameter('code'))
        if not assertion:
            raise gen.Return(Response(msg=RESP_IDENTITY_INCOMPLETE))

        logged = LoginService().login(assertion, self.getRequestParameter('shareOpenid'))
        if not logged:
            raise gen.Return(Response(msg=RESP_IDENTITY_INCOMPLETE))
        access_token, sign_secret, openid, phone_bound = logged
        data = {
            'accessToken': access_token,
            'secret': sign_secret,
            'phoneBound': phone_bound,
        }
        if openid:
            data['openid'] = openid
        raise gen.Return(Response(data=data))

    @superMonitor
    def put(self, *args, **kwargs):
        """用户退出登录"""
        delSession(self.accessToken)
        return Response()
