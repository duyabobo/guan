#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.common.phone_number import PHONE_CODE_RESEND_SEC
from service.phone_bind import PhoneBindService
from service.phone_code import PhoneCodeService
from util.const.response import (
    RESP_PHONE_BIND_FAILED,
    RESP_PHONE_CODE_TOO_SOON,
    RESP_PHONE_INVALID,
    RESP_SMS_UNAVAILABLE,
)
from util.monitor import superMonitor, Response

_SEND_MSG = {
    'invalid': RESP_PHONE_INVALID,
    'soon': RESP_PHONE_CODE_TOO_SOON,
    'unconfigured': RESP_SMS_UNAVAILABLE,
}


class PhoneCodeHandler(BaseHandler):

    @superMonitor
    def post(self, *args, **kwargs):
        outcome = PhoneCodeService().send(
            self.currentPassportId,
            self.getRequestParameter('phone', default=''),
        )
        msg = _SEND_MSG.get(outcome)
        if msg:
            return Response(msg=msg)
        return Response(data={'retryAfter': PHONE_CODE_RESEND_SEC})


class PhoneHandler(BaseHandler):

    @superMonitor
    def post(self, *args, **kwargs):
        bound = PhoneBindService().bind(
            self.currentPassportId,
            self.getRequestParameter('phone', default=''),
            self.getRequestParameter('code', default=''),
        )
        if not bound:
            return Response(msg=RESP_PHONE_BIND_FAILED)
        return Response(data={'phoneBound': True})
