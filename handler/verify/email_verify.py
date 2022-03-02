#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.email_verify import EmailVerifyService
from util.monitor import superMonitor


class EmailVerifyHandler(BaseHandler):

    @superMonitor
    def get(self):
        email = self.getRequestParameter('email')
        evs = EmailVerifyService(self.dbSession, self.redis)
        evs.sendVerifyEmail(self.currentPassportId, email)
        return self.response()

    @superMonitor
    def put(self, *args, **kwargs):
        # todo 验证邮件
        return self.response()
