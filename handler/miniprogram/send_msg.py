# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2024/5/9 22:52
#  File: send_msg.py
#  Software: PyCharm
from tornado import gen

from handler.basehandler import BaseHandler
from util.monitor import superGenMonitor
from util.wx_mini import WxHelper


# 发送客服消息
class SendSmsHandler(BaseHandler):

    # @superGenMonitor
    @gen.coroutine
    def get(self):
        openid = self.getRequestParameter('openid', '')
        msgContent = self.getRequestParameter('msgContent', '')
        ret = yield WxHelper().sendMsgToUser(openid, msgContent)
        self.write({'ret': str(ret)})

