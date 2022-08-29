#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from tornado import gen

from handler.basehandler import BaseHandler
from ral.passport import delSession
from service.login import LoginService
from util.const.response import RESP_NEED_LOGIN
from util.monitor import superMonitor, Response
from util.wx_mini import WxHelper


class LoginHandler(BaseHandler):
    __model__ = ''

    @gen.coroutine
    def get(self, *args, **kwargs):
        """微信登录注册接口
        """
        jsCode = self.getRequestParameter('code')
        shareOpenid = self.getRequestParameter('shareOpenid')
        openid = yield WxHelper().getOpenidByCode(jsCode)
        if not openid:
            self.response(Response(msg=RESP_NEED_LOGIN))
            return

        accessToken, secret = LoginService().login(openid, shareOpenid)
        self.response(Response(data={
            'accessToken': accessToken,
            'secret': secret,
            'openid': openid,
        }))
        return

    @superMonitor
    def put(self, *args, **kwargs):
        """用户退出登录
        """
        delSession(self.accessToken)
        return Response()
