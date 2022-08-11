#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guanguan import GuanguanService
from util.monitor import superMonitor


class GuanguanHandler(BaseHandler):

    @superMonitor
    def get(self):
        longitude = self.getRequestParameter('longitude', paraType=float)
        latitude = self.getRequestParameter('latitude', paraType=float)
        ggs = GuanguanService(self.currentPassportId)
        return self.response(
            {
                "guanguanList": ggs.getGuanguanList(longitude, latitude),
            }
        )
