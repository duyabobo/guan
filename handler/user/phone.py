#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.phone_bind import PhoneBindService
from util.const.response import RESP_PHONE_BIND_FAILED
from util.monitor import superMonitor, Response


class PhoneHandler(BaseHandler):

    @superMonitor
    def post(self, *args, **kwargs):
        """已登录用户补绑手机号。号码来自微信手机号按钮的一次性 code。"""
        phone_code = self.getRequestParameter('phoneCode', default='')
        if not phone_code or not self.currentPassportId:
            return Response(msg=RESP_PHONE_BIND_FAILED)
        if not PhoneBindService().bind(self.currentPassportId, phone_code):
            return Response(msg=RESP_PHONE_BIND_FAILED)
        return Response(data={'phoneBound': True})
