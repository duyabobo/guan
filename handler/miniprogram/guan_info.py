#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guan_info import GuanInfoService
from util.monitor import superMonitor, Response


class GuanInfoHandler(BaseHandler):

    @superMonitor
    def get(self):
        activityId = self.getRequestParameter('guanId', paraType=int)
        gis = GuanInfoService(activityId, self.currentPassport)
        return Response(data=gis.getGuanInfo())

    @superMonitor
    def put(self, *args, **kwargs):
        activityId = self.getRequestParameter('guanId', paraType=int)
        opType = self.getRequestParameter('opType', paraType=int)
        gis = GuanInfoService(activityId, self.currentPassport)
        ret = gis.activityOprete(opType)
        gis.updateMyInformationPage(ret)
        return Response(data=gis.getGuanInfo(), msg=ret)


class MeetResultHandler(BaseHandler):

    @superMonitor
    def put(self, *args, **kwargs):
        activityId = self.getRequestParameter('guanId', paraType=int)
        meetResultValue = self.getRequestParameter('value', paraType=int)
        gis = GuanInfoService(activityId, self.currentPassport)
        ret = gis.updateMeetResult(meetResultValue)
        return Response(msg=ret)
