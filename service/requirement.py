#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.match import MatchHelper
from model.requirement import RequirementModel
from model.user import UserModel
from service import BaseService
from util import const
from util.class_helper import lazy_property


class RequirementService(BaseService):

    def __init__(self, dbSession, redis, passportId):
        self.dbSession = dbSession
        self.redis = redis
        self.passportId = passportId
        self.matchHelper = MatchHelper(self.requirementInfo, isUserNotRequirement=False)
        super(RequirementService, self).__init__(dbSession, redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.dbSession, self.passportId)

    @lazy_property
    def requirementInfo(self):
        return RequirementModel.getByPassportId(self.dbSession, self.passportId)

    def reloadMatchHelper(self):
        requirementInfo = RequirementModel.getByPassportId(self.dbSession, self.passportId)
        self.matchHelper = MatchHelper(requirementInfo, isUserNotRequirement=False)

    def getRequirementInfo(self):
        return {
            "sex": self.matchHelper.getSexInfo(),
            "birthYear": self.matchHelper.getRequirementBirthYearInfo(),
            "weight": self.matchHelper.getRequirementWeight(),
            "height": self.matchHelper.getRequirementHeight(),
            "monthPay": self.matchHelper.getRequirementMonthPay(),
            "otherRequirementList": self.matchHelper.getOtherInfoList(),
        }

    def updateRequirementInfo(self, opType, value):
        updateParams = self.matchHelper.getUpdateParams(opType, value)
        if updateParams:
            RequirementModel.updateByPassportId(self.dbSession, self.passportId, **updateParams)
            self.reloadMatchHelper()
        return self.getRequirementInfo()

    def checkBeforeUpdate(self, opType, value):
        if opType == const.MODEL_USER_OP_TYPE_SEX and not self.userInfo.sex:
            return const.RESP_USER_SEX_FIRST_EDIT
        if opType == const.MODEL_USER_OP_TYPE_SEX and int(value) == self.userInfo.sex:
            return const.RESP_REQUIREMENT_SEX_ERROR
        # todo 其他修改限制半年一次修改机会
