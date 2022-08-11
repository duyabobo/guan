#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from ral.email_verify import EmailVerifyService
from service.myself import UserInfoService
from util.monitor import superMonitor


class EmailVerifyHandler(BaseHandler):

    @superMonitor
    def get(self):
        email = self.getRequestParameter('email')
        evs = EmailVerifyService(self.currentPassportId)
        ret = evs.sendVerifyEmail(email)
        return self.response(respNormal=ret)

    @superMonitor
    def put(self, *args, **kwargs):
        email = self.getRequestParameter('email')
        code = self.getRequestParameter('code')
        evs = EmailVerifyService(self.currentPassportId)
        ret = evs.checkCodeWithCache(email, code)
        uis = UserInfoService(self.currentPassport)
        return self.response(respData=uis.getMyselfInfo(), respNormal=ret)
