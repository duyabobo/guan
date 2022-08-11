#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.common.selector import VALUE_TYPE_DICT
from service.requirement import RequirementService
from util.monitor import superMonitor


class RequirementHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        ris = RequirementService(self.currentPassportId)
        return self.response(
            respData=ris.getRequirementInfo()
        )

    @superMonitor
    def put(self, *args, **kwargs):
        opType = self.getRequestParameter('opType')
        column = self.getRequestParameter('column', paraType=int)
        valueType = VALUE_TYPE_DICT[opType]
        value = self.getRequestParameter('value', paraType=valueType)

        ris = RequirementService(self.currentPassportId)
        ret = ris.checkBeforeUpdate(opType, value)
        if ret:
            return self.response(
                respNormal=ret
            )
        return self.response(
            respData=ris.updateRequirementInfo(opType, value, column)
        )
