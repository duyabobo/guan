#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor


class AboutHandler(BaseHandler):
    @superMonitor
    def get(self):
        return self.response(
            {
                "title": "关关雎鸠介绍",
                "descList": []  # todo
            }
        )
