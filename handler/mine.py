#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor 

from service.mine import MineService


class MineHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        headImg = MineService(self.dbSession, self.redis).getHeadImg(self.currentPassportId)
        return self.response(
            respData={'headImg': headImg}
        )
