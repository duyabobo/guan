# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2024/5/8 22:51
#  File: contact.py
#  Software: PyCharm
from handler.basehandler import BaseHandler
from service.mine import MineService
from util.monitor import superMonitor, Response


class ContactHandler(BaseHandler):
    @superMonitor
    def post(self, *args, **kwargs):
        ToUserName = self.getRequestParameter('ToUserName', '')
        FromUserName = self.getRequestParameter('FromUserName', '')
        CreateTime = self.getRequestParameter('CreateTime', 0)
        MsgType = self.getRequestParameter('MsgType', '')
        Content = self.getRequestParameter('Content', '')
        MsgId = self.getRequestParameter('MsgId', '')

        return Response()
