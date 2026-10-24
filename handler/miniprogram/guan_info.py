#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guan_info import GuanInfoService
from util.const.progress import MEET_VIEWER_MODE
from util.monitor import superMonitor, Response


class GuanInfoHandler(BaseHandler):

    @superMonitor
    def get(self):
        activityId = self.getRequestParameter('guanId', paraType=int)
        viewer = self.getRequestParameter('viewer', default=0, paraType=int)
        gis = GuanInfoService(activityId, self.currentPassport)
        if viewer == MEET_VIEWER_MODE:
            share_openid = self.getRequestParameter('shareOpenid', '')
            return Response(data=gis.getViewerGuanInfo(share_openid))
        return Response(data=gis.getGuanInfo())

    @superMonitor
    def put(self, *args, **kwargs):
        activityId = self.getRequestParameter('guanId', paraType=int)
        opType = self.getRequestParameter('opType', paraType=int)
        gis = GuanInfoService(activityId, self.currentPassport)
        openid = self.getRequestParameter('openid', '')
        ret = gis.activityOprete(opType, openid, self.request.remote_ip or '')
        gis.updateMyInformationPage(ret)
        data = gis.getGuanInfo()
        if gis.pending_pay:
            data['pay'] = gis.pending_pay
        return Response(data=data, msg=ret)


class MeetResultHandler(BaseHandler):

    @superMonitor
    def put(self, *args, **kwargs):
        activityId = self.getRequestParameter('guanId', paraType=int)
        meetResultValue = self.getRequestParameter('value', paraType=int)
        gis = GuanInfoService(activityId, self.currentPassport)
        ret = gis.updateMeetResult(meetResultValue)
        return Response(msg=ret)
