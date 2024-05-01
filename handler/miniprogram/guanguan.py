#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guanguan import GuanguanService, UNKNOWN_LONGITUDE_OR_LATITUDE
from util.monitor import superMonitor, Response
from util.time_cost import timecost


class GuanguanHandler(BaseHandler):

    @superMonitor
    @timecost
    def get(self):
        longitude = self.getRequestParameter('longitude', default=UNKNOWN_LONGITUDE_OR_LATITUDE, paraType=float)
        latitude = self.getRequestParameter('latitude', default=UNKNOWN_LONGITUDE_OR_LATITUDE, paraType=float)
        limit = self.getRequestParameter('limit', paraType=int, default=20)
        ggs = GuanguanService(self.currentPassportId)
        return Response(data={
            "guanguanList": ggs.getGuanguanList(longitude, latitude, limit),
        })
