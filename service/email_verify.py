#! /usr/bin/env python
# -*- coding: utf-8 -*-
from service import BaseService


class EmailVerifyService(BaseService):

    def sendVerifyEmail(self, passportId, email):
        """每六个月只能收到一次"""
        pass  # todo 发送邮件逻辑
