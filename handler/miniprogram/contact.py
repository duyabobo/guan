# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2024/5/8 22:51
#  File: contact.py
#  Software: PyCharm
import util.config
from handler.basehandler import BaseHandler
from service.wx_crypt.WXBizMsgCrypt import WXBizMsgCrypt
from util.monitor import superMonitor, Response


class ContactHandler(BaseHandler):
    
    # @superMonitor
    def get(self):
        echostr = self.getRequestParameter('echostr', '')
        # todo 校验是否来自微信
        return self.write(echostr)

    # todo 特殊的monitor
    @superMonitor
    def post(self, *args, **kwargs):
        signature = self.getRequestParameter('signature', '')
        timestamp = self.getRequestParameter('timestamp', '')
        nonce = self.getRequestParameter('nonce', '')
        encrypt_type = self.getRequestParameter('encrypt_type', '')
        msgSign = self.getRequestParameter('msg_signature', '')
        ToUserName = self.getRequestParameter('ToUserName', '')
        FromUserName = self.getRequestParameter('FromUserName', '')
        CreateTime = self.getRequestParameter('CreateTime', '')
        MsgType = self.getRequestParameter('MsgType', '')
        Content = self.getRequestParameter('Content', '')
        MsgId = self.getRequestParameter('MsgId', '')
        Encrypt = self.getRequestParameter('Encrypt', '')
        return Response(data={'ret': 0})
