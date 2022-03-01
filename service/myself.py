#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.match import MatchHelper
from model.user import UserModel
from service import BaseService
from util.class_helper import lazy_property
from model.verify import VerifyModel
from util import const


class UserInfoService(BaseService):

    def __init__(self, dbSession, redis, currentPassport):
        self.dbSession = dbSession
        self.redis = redis
        self.currentPassport = currentPassport
        self.passportId = currentPassport.get('id', 0)
        self.matchHelper = MatchHelper(self.userInfo)
        super(UserInfoService, self).__init__(dbSession, redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.dbSession, self.passportId)

    def getWork(self):
        verify = VerifyModel.getByPassportId(self.dbSession, self.passportId)
        return {
            "desc": "工作认证",
            "value": "已认证" if verify.work_verify_status == const.MODEL_WORK_VERIFY_STATUS_YES else "未认证",
        }

    def getPhone(self):
        return {
            "desc": "手机认证",
            "value": "已认证" if self.currentPassport.get('phone', '') else "未认证",
        }

    def reloadMatchHelper(self):
        userInfo = UserModel.getByPassportId(self.dbSession, self.passportId)
        self.matchHelper = MatchHelper(userInfo)

    def getMyselfInfo(self):
        return {
            "phoneVerify": self.getPhone(),
            "workVerify": self.getWork(),
            "sex": self.matchHelper.getSexInfo(),
            "birthYear": self.matchHelper.getBirthYearInfo(),
            "weight": self.matchHelper.getWeight(),
            "monthPay": self.matchHelper.getMonthPay(),
            "height": self.matchHelper.getHeight(),
            "otherInfoList": self.matchHelper.getOtherInfoList(),
        }

    def updateMyselfInfo(self, opType, value):
        updateParams = self.matchHelper.getUpdateParams(opType, value)
        if updateParams:
            UserModel.updateByPassportId(self.dbSession, self.passportId, **updateParams)
            # todo 自动填充一下需求信息
            self.reloadMatchHelper()
        return self.getMyselfInfo()
