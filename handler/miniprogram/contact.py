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

    # todo 特殊的monitor
    @superMonitor
    def post(self, *args, **kwargs):
        signature = self.request.query_arguments.get('signature', '')
        timestamp = self.request.query_arguments.get('timestamp', '')
        nonce = self.request.query_arguments.get('nonce', '')
        encrypt_type = self.request.query_arguments.get('encrypt_type', '')
        msgSign = self.request.query_arguments.get('msg_signature', '')
        from_xml = self.request.body_arguments or self.request.body
        appid = util.config.get('weixin', 'appid')
        token = util.config.get('weixin', 'token')
        encodingAESKey = util.config.get('weixin', 'encodingAESKey')
        decrypt_test = WXBizMsgCrypt(token, encodingAESKey, appid)
        ret, decrypXml = decrypt_test.DecryptMsg(from_xml, msgSign, timestamp, nonce)
        return Response(data={'ret': ret, 'decrypXml': decrypXml})
