#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.match import matchHelper
from model.user import UserModel
from service import BaseService
from util.class_helper import lazy_property


class UserInfoService(BaseService):

    def __init__(self, dbSession, redis, passportId):
        self.dbSession = dbSession
        self.redis = redis
        self.passportId = passportId
        self.matchHelper = matchHelper(self.userInfo)
        super(UserInfoService, self).__init__(dbSession, redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.dbSession, self.passportId)

    def reloadMatchHelper(self):
        userInfo = UserModel.getByPassportId(self.dbSession, self.passportId)
        self.matchHelper = matchHelper(userInfo)

    def getMyselfInfo(self):
        return {
            "sex": self.matchHelper.getSexInfo(),
            "birthYear": self.matchHelper.getbirthYearInfo(),
            "otherInfoList": self.matchHelper.getOtherInfoList(),
        }

    def updateMyselfInfo(self, opType, value):
        updateParams = self.matchHelper.getUpdateParams(opType, value)
        if updateParams:
            UserModel.updateByPassportId(self.dbSession, self.passportId, **updateParams)
            self.reloadMatchHelper()
        return self.getMyselfInfo()
