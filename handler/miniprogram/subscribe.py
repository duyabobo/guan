#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from handler.basehandler import BaseHandler
from service.meet_notice import MeetNoticeService
from util.monitor import superMonitor, Response


class SubscribeCBHandler(BaseHandler):
    @superMonitor
    def post(self, *args, **kwargs):
        """用户点了订阅。接受后增加一次可发送额度，openid 加密保存。"""
        body = _json_body(self.request.body)
        MeetNoticeService.accept(
            self.currentPassportId,
            body.get('openid') or '',
            body.get('subscribeRes') or {},
        )
        return Response()


def _json_body(raw):
    if not raw:
        return {}
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8')
    loaded = json.loads(raw)
    if isinstance(loaded, dict):
        return loaded
    return {}
