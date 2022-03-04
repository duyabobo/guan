#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from util.monitor import superMonitor

from service.myself import UserInfoService


class MyselfHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        uis = UserInfoService(self.dbSession, self.redis, self.currentPassport)
        return self.response(
            respData=uis.getMyselfInfo()
        )

    @superMonitor
    def put(self, *args, **kwargs):
        opType = self.getRequestParameter('opType', paraType=int)
        value = self.getRequestParameter('value')

        uis = UserInfoService(self.dbSession, self.redis, self.currentPassport)
        ret = uis.checkBeforeUpdate(opType, value)
        if ret:
            return self.response(
                respNormal=ret
            )
        return self.response(
            respData=uis.updateMyselfInfo(opType, value)
        )
