#! /usr/bin/env python
# -*- coding: utf-8 -*-
from handler.basehandler import BaseHandler
from service.guanguan import GuanguanService
from util import const
from util.monitor import superMonitor


class GuanguanHandler(BaseHandler):

    @superMonitor
    def get(self):
        longitude = self.getRequestParameter('longitude', paraType=float)
        latitude = self.getRequestParameter('latitude', paraType=float)
        ggs = GuanguanService(self.dbSession, self.redis, self.currentPassportId)
        return self.response(
            {
                "guanguanList": ggs.getGuanguanList(longitude, latitude),
                "myRequirementPage": const.MYREQUIREMENT_PAGE,
                "requirementResult": "供37人符合您的择偶条件"  # todo
            }
        )
