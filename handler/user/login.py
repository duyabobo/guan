#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from tornado import gen

from handler.basehandler import BaseHandler
from ral.passport import delSession
from service.identity.registry import get_provider
from service.login import LoginService
from util.const.identity import PROVIDER_WECHAT
from util.const.response import RESP_IDENTITY_INCOMPLETE, RESP_NEED_LOGIN
from util.monitor import superMonitor, Response, superGenMonitor


class LoginHandler(BaseHandler):
    __model__ = ''

    @superGenMonitor
    @gen.coroutine
    def get(self, *args, **kwargs):
        """登录。默认微信，后续国家网络身份认证走同一个入口。"""
        provider_code = self.getRequestParameter('provider', PROVIDER_WECHAT)
        provider = get_provider(provider_code)
        if not provider:
            raise gen.Return(Response(msg=RESP_NEED_LOGIN))

        assertion = yield provider.authenticate(self.getRequestParameter('code'))
        if not assertion:
            raise gen.Return(Response(msg=RESP_IDENTITY_INCOMPLETE))

        logged = LoginService().login(
            assertion,
            self.getRequestParameter('shareOpenid'),
            self.getRequestParameter('phoneCode', default=''),
        )
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
