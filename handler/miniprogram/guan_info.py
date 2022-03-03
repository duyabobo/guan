#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guan_info import GuanInfoService
from util.monitor import superMonitor


class GuanInfoHandler(BaseHandler):

    @superMonitor
    def get(self):
        activityId = self.getRequestParameter('guanId', paraType=int)
        gis = GuanInfoService(self.dbSession, self.redis, activityId, self.currentPassportId)
        return self.response(gis.getGuanInfo())

    @superMonitor
    def put(self, *args, **kwargs):
        activityId = self.getRequestParameter('guanId', paraType=int)
        opType = self.getRequestParameter('opType', paraType=int)
        gis = GuanInfoService(self.dbSession, self.redis, activityId, self.currentPassportId)
        gis.activityOprete(opType)
        return self.response(gis.getGuanInfo())