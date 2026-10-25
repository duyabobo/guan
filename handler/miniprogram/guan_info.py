#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guan_info import GuanInfoService
from util.const.base import (
    GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_QUIT,
    MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE,
)
from util.const.progress import MEET_VIEWER_MODE
from util.monitor import superMonitor, Response


_OP_TYPES = (GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_QUIT)
_MEET_RESULT_CHOICES = (MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE)
_ID_MIN = 1


class GuanInfoHandler(BaseHandler):

    @superMonitor
    def get(self):
        activityId = self.getIntParameter('guanId', minimum=_ID_MIN)
        viewer = self.getRequestParameter('viewer', default=0, paraType=int)
        gis = GuanInfoService(activityId, self.currentPassport)
        if viewer == MEET_VIEWER_MODE:
            share_openid = self.getRequestParameter('shareOpenid', '')
            return Response(data=gis.getViewerGuanInfo(share_openid))
        return Response(data=gis.getGuanInfo())

    @superMonitor
    def put(self, *args, **kwargs):
        activityId = self.getIntParameter('guanId', minimum=_ID_MIN)
        opType = self.getIntParameter('opType', choices=_OP_TYPES)
        gis = GuanInfoService(activityId, self.currentPassport)
        ret = gis.activityOprete(opType)
        gis.updateMyInformationPage(ret)
        return Response(data=gis.getGuanInfo(), msg=ret)


class MeetResultHandler(BaseHandler):

    @superMonitor
    def put(self, *args, **kwargs):
        activityId = self.getIntParameter('guanId', minimum=_ID_MIN)
        meetResultValue = self.getIntParameter('value', choices=_MEET_RESULT_CHOICES)
        gis = GuanInfoService(activityId, self.currentPassport)
        ret = gis.updateMeetResult(meetResultValue)
        return Response(msg=ret)
