#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""微信支付结果通知。微信服务器调用，不走登录签名。"""
from handler.basehandler import BaseHandler
from service.meet_fee import MeetFeeService


class WxPayNotifyHandler(BaseHandler):

    def post(self):
        xml = MeetFeeService.handle_notify(self.request.body)
        try:
            self.set_header('Content-Type', 'text/xml; charset=utf-8')
            self.write(xml)
            self.dbSession.commit()
        finally:
            self.dbSession.close()
