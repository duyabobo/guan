#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.mine import MineService
from util.monitor import superMonitor, Response


class MineHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        ms = MineService()
        headImg = ms.getHeadImg(self.currentPassportId)
        mainGroupList = ms.getMainGroupList()

        hasLogin = False
        if self.accessToken:
            hasLogin = True
        return Response(data={
            'headImg': headImg,
            'hasLogin': hasLogin,
            'mainGroupList': mainGroupList,
        })
