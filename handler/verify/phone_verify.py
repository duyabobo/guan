#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor


class PhoneVerifyHandler(BaseHandler):

    @superMonitor
    def get(self):
        return self.response()

    @superMonitor
    def put(self, *args, **kwargs):
        # todo 验证手机号
        return self.response()
