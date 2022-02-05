#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from handler.basehandler import BaseHandler
from ral.passport import delCurrentUserInfo
from service.login import WxHelper, LoginService
from util.const import RESP_NEED_LOGIN
from util.monitor import superMonitor


class LoginHandler(BaseHandler):
    __model__ = ''

    @superMonitor
    def get(self, *args, **kwargs):
        """微信登录注册接口
        """
        jsCode = self.getRequestParameter('code')
        openid = WxHelper.getOpenidByCode(jsCode)
        if not openid:
            return self.response(respNormal=RESP_NEED_LOGIN)

        accessToken, currentUserInfo = LoginService(self.dbSession, self.redis).login(openid)
        return self.response(
            respJson={'accessToken': accessToken, 'currentUserInfo': currentUserInfo}
        )

    @superMonitor
    def put(self, *args, **kwargs):
        """用户退出登录
        """
        delCurrentUserInfo(self.redis, self.accessToken)
        return self.response()
