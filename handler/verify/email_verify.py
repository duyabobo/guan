#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from ral.email_verify import EmailVerifyService
from service.myself import UserInfoService
from util.monitor import superMonitor, Response


class EmailVerifyHandler(BaseHandler):

    @superMonitor
    def get(self):
        openid = self.getRequestParameter('openid')
        email = self.getRequestParameter('email')
        evs = EmailVerifyService(self.currentPassport)
        ret = evs.sendVerifyEmail(openid, email)
        return Response(msg=ret)

    @superMonitor
    def put(self, *args, **kwargs):
        openid = self.getRequestParameter('openid')
        email = self.getRequestParameter('email')
        code = self.getRequestParameter('code')
        evs = EmailVerifyService(self.currentPassport)
        ret = evs.checkCodeWithCache(openid, email, code)
        uis = UserInfoService(self.currentPassport)
        return Response(data=uis.getMyselfInfo(), msg=ret)
