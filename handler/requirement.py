#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.requirement import RequirementService
from util.monitor import superMonitor


class RequirementHandler(BaseHandler):
    @superMonitor
    def get(self, *args, **kwargs):
        ris = RequirementService(self.dbSession, self.redis, self.currentPassportId)
        return self.response(
            respData=ris.getRequirementInfo()
        )

    @superMonitor
    def put(self, *args, **kwargs):
        opType = self.getRequestParameter('opType', paraType=int)
        value = self.getRequestParameter('value')
        ris = RequirementService(self.dbSession, self.redis, self.currentPassportId)
        return self.response(
            respData=ris.updateRequirementInfo(opType, value)
        )
