#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor

from service.myself import userInfoService


class MyselfHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        uis = userInfoService(self.dbSession, self.redis, self.currentPassportId)
        return self.response(
            respJson=uis.getMyselfInfo()
        )

    @superMonitor
    def put(self, *args, **kwargs):
        opType = self.getRequestParameter('opType', paraType=int)
        value = self.getRequestParameter('value')
        uis = userInfoService(self.dbSession, self.redis, self.currentPassportId)
        return self.response(
            respJson=uis.updateMyselfInfo(opType, value)
        )
