# -*- coding: utf-8 -*-
#  Author: duyabo
#  Time : 2024/5/8 22:51
#  File: contact.py
#  Software: PyCharm
import util.config
from handler.basehandler import BaseHandler
from service.mine import MineService
from service.wx_crypt.WXBizMsgCrypt import WXBizMsgCrypt
from util.monitor import superMonitor, Response, httpReturn


class ContactHandler(BaseHandler):

    def post(self, *args, **kwargs):
        signature = self.getRequestParameter('signature')
        timestamp = self.getRequestParameter('timestamp')
        nonce = self.getRequestParameter('nonce')
        encrypt_type = self.getRequestParameter('encrypt_type')
        msgSign = self.getRequestParameter('msg_signature')
        from_xml = self.request.body_arguments or self.request.body
        appid = util.config.get('weixin', 'appid')
        token = util.config.get('weixin', 'token')
        encodingAESKey = util.config.get('weixin', 'encodingAESKey')
        decrypt_test = WXBizMsgCrypt(token, encodingAESKey, appid)
        ret, decrypXml = decrypt_test.DecryptMsg(from_xml, msgSign, timestamp, nonce)
        response = Response(data={'ret': ret, 'decrypXml': decrypXml})
        httpReturn(self, response)
        return
