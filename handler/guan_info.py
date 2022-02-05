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
        return self.response(
            {
                "img": gis.img,
                "address": gis.address,
                "address_desc": gis.addressDesc,
                "time": gis.time,
                "time_desc": gis.timeDesc,
                "personInfos": gis.personInfos,
                "opDesc": gis.opDesc,
                "opType": gis.opType,
                "timeImg": gis.timeIcon,
                "addressImg": gis.addressIcon,
                "personImg": gis.personIcon,
            }
        )
