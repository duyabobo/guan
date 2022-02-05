#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.requirement import RequirementModel

from common.match import matchHelper
from service import BaseService
from util.class_helper import lazy_property


class RequirementService(BaseService):

    def __init__(self, dbSession, redis, passportId):
        self.dbSession = dbSession
        self.redis = redis
        self.passportId = passportId
        self.matchHelper = matchHelper(self.requirementInfo)
        super(RequirementService, self).__init__(dbSession, redis)

    @lazy_property
    def requirementInfo(self):
        return RequirementModel.getByPassportId(self.dbSession, self.passportId)

    def reloadMatchHelper(self):
        requirementInfo = RequirementModel.getByPassportId(self.dbSession, self.passportId)
        self.matchHelper = matchHelper(requirementInfo)

    def getRequirementInfo(self):
        return {
            "sex": self.matchHelper.getSexInfo(),
            "birthYear": self.matchHelper.getbirthYearInfo(),
            "otherRequirementList": self.matchHelper.getOtherInfoList(),
        }

    def updateRequirementInfo(self, opType, value):
        updateParams = self.matchHelper.getUpdateParams(opType, value)
        if updateParams:
            RequirementModel.updateByPassportId(self.dbSession, self.passportId, **updateParams)
            self.reloadMatchHelper()
        return self.getRequirementInfo()