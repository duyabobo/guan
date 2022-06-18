#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.requirement import RequirementService
from util.monitor import superMonitor


class RequirementHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        ris = RequirementService(self.redis, self.currentPassportId)
        return self.response(
            respData=ris.getRequirementInfo()
        )

    @superMonitor
    def put(self, *args, **kwargs):
        opType = self.getRequestParameter('opType')
        valueIndex = self.getRequestParameter('value')

        ris = RequirementService(self.redis, self.currentPassportId)
        ret = ris.checkBeforeUpdate(opType, valueIndex)
        if ret:
            return self.response(
                respNormal=ret
            )
        return self.response(
            respData=ris.updateRequirementInfo(opType, valueIndex)
        )
