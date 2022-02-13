#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.match import MatchHelper
from model.user import UserModel
from service import BaseService
from util.class_helper import lazy_property
from model.verify import VerifyModel
from util import const


class UserInfoService(BaseService):

    def __init__(self, dbSession, redis, passportId):
        self.dbSession = dbSession
        self.redis = redis
        self.passportId = passportId
        self.matchHelper = MatchHelper(self.userInfo)
        super(UserInfoService, self).__init__(dbSession, redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.dbSession, self.passportId)

    def getVerify(self):
        verify = VerifyModel.getByPassportId(self.dbSession, self.passportId)
        return {
            "opType": const.MODEL_USER_OP_TYPE_VERIFY,
            "desc": "工作认证",
            "value": "已认证" if verify.work_verify_status == const.MODEL_WORK_VERIFY_STATUS_YES else "未认证",
        }

    def reloadMatchHelper(self):
        userInfo = UserModel.getByPassportId(self.dbSession, self.passportId)
        self.matchHelper = MatchHelper(userInfo)

    def getMyselfInfo(self):
        return {
            "verify": self.getVerify(),
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
