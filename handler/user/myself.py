#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.common.selector import VALUE_TYPE_DICT
from service.myself import UserInfoService
from util.monitor import superMonitor


class MyselfHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        uis = UserInfoService(self.currentPassport)
        return self.response(
            respData=uis.getMyselfInfo()
        )

    @superMonitor
    def put(self, *args, **kwargs):
        opType = self.getRequestParameter('opType')
        column = self.getRequestParameter('column', paraType=int)
        valueType = VALUE_TYPE_DICT[opType]
        value = self.getRequestParameter('value', paraType=valueType)

        uis = UserInfoService(self.currentPassport)
        ret = uis.checkBeforeUpdate(opType, value)
        if ret:
            return self.response(
                respNormal=ret
            )
        return self.response(
            respData=uis.updateMyselfInfo(opType, value, column=column)
        )
