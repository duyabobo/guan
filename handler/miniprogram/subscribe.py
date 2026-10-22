#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tornado import gen

from handler.basehandler import BaseHandler
from util.monitor import superMonitor, Response


class SubscribeCBHandler(BaseHandler):
    @superMonitor
    def post(self, *args, **kwargs):
        """小程序订阅结果回调。当前不落库，保留接口避免客户端报错。"""
        return Response()
