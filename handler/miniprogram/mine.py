#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.mine import MineService
from util.monitor import superMonitor


class MineHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        ms = MineService(self.dbSession, self.redis)
        headImg = ms.getHeadImg(self.currentPassportId)
        mainGroupList = ms.getMainGroupList()

        hasLogin = False
        if self.accessToken:
            hasLogin = True
        return self.response(
            respData={
                'headImg': headImg,
                'hasLogin': hasLogin,
                'mainGroupList': mainGroupList,
            }
        )
