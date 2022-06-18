#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor


class SecretHandler(BaseHandler):
    @superMonitor
    def get(self):
        return self.response(
            {
                "title": "隐私条款",
                "descList": []
            }
        )
