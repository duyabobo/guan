#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guanguan import GuanguanService
from util.monitor import superMonitor, Response


class GuanguanHandler(BaseHandler):

    @superMonitor
    def get(self):
        shareOpenid = self.getRequestParameter('shareOpenid')  # 分享人openid
        longitude = self.getRequestParameter('longitude', paraType=float)
        latitude = self.getRequestParameter('latitude', paraType=float)
        ggs = GuanguanService(self.currentPassportId)
        return Response(data={
            "guanguanList": ggs.getGuanguanList(longitude, latitude),
        })
