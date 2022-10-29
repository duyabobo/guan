#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guanguan import GuanguanService
from util.monitor import superMonitor, Response
from util.time_cost import timecost


class GuanguanHandler(BaseHandler):

    @superMonitor
    @timecost
    def get(self):
        longitude = self.getRequestParameter('longitude', paraType=float)
        latitude = self.getRequestParameter('latitude', paraType=float)
        ggs = GuanguanService(self.currentPassportId)
        return Response(data={
            "guanguanList": ggs.getGuanguanList(longitude, latitude),
        })
