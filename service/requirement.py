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
            "requirementList": [
                self.matchHelper.getSexInfo(),
                self.matchHelper.getBirthYearPeriod(),
                self.matchHelper.getHeightPeriod(),
                self.matchHelper.getWeightPeriod(),
                self.matchHelper.getMonthPayPeriod(),
                self.matchHelper.getMartialStatusPeriod(),
                self.matchHelper.getEducationPeriod(),
            ],
            "columnChangeTypeIndexMap": {  # 给requirementList的每个元素一个对应序号
                "sex": 0,
                "birthYearPeriod": 1,
                "heightPeriod": 2,
                "weightPeriod": 3,
                "monthPayPeriod": 4,
                "martialStatus": 5,
                "educationPeriod": 6,
            },
            "requirementResult": "3人满足见面条件"  # todo
        }

    def updateRequirementInfo(self, opType, valueIndex):
        updateParams = self.matchHelper.getUpdateParams(opType, valueIndex)
        if updateParams:
            RequirementModel.updateByPassportId(self.dbSession, self.passportId, **updateParams)
            self.reloadMatchHelper()
        return self.getRequirementInfo()  # todo 可以扩展需要支持返回成功+提醒的code码

    def checkBeforeUpdate(self, opType, valueIndex):
        if opType == const.MODEL_USER_OP_TYPE_SEX and self.userInfo.sex == const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST[const.MODEL_USER_OP_TYPE_DEFAULT_SEX_INDEX]:
            return const.RESP_USER_SEX_FIRST_EDIT
        if opType == const.MODEL_USER_OP_TYPE_SEX and int(valueIndex) == const.MODEL_USER_OP_TYPE_SEX_CHOICE_LIST.index(self.userInfo.sex):
            return const.RESP_REQUIREMENT_SEX_ERROR
        # todo 其他修改限制半年一次修改机会
