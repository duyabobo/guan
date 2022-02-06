#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util import const
from util.monitor import superMonitor


class AboutHandler(BaseHandler):
    @superMonitor
    def get(self):
        return self.response(
            {
                "realLogoUrl": const.CDN_QINIU_URL + '/real_logo.png',
                "version": "v2.0"
            }
        )
