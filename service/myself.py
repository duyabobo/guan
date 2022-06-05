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

    @property
    def verify(self):
        return VerifyModel.getByPassportId(self.dbSession, self.passportId)

    @property
    def isVerified(self):
        return self.verify.work_verify_status == const.MODEL_WORK_VERIFY_STATUS_YES

    @property
    def infoIsFilled(self):
        return self.userInfo.sex and self.userInfo.birth_year \
               and self.userInfo.martial_status and self.userInfo.height \
               and self.userInfo.weight and self.userInfo.month_pay and self.userInfo.education

    @property
    def userInfoIsFilled(self):
        return self.isVerified and self.infoIsFilled

    def getWork(self):
        return {
            "desc": "工作认证",
            "value": "已认证" if self.verify.work_verify_status == const.MODEL_WORK_VERIFY_STATUS_YES else "未认证",
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
        informationList = [
            self.matchHelper.getSexInfo(),
            self.matchHelper.getBirthYearInfo(),
            self.matchHelper.getHeight(),
            self.matchHelper.getWeight(),
            self.matchHelper.getMonthPay(),
            self.matchHelper.getMartialStatus(),
            self.matchHelper.getEducation(),
        ]
        columnChangeTypeIndexMap = {v.get('bindColumnChange', ''): i for i, v in enumerate(informationList)}
        return {
            "informationList": informationList,
            "columnChangeTypeIndexMap": columnChangeTypeIndexMap,  # 给informationList的每个元素一个对应序号
            "workVerify": self.getWork(),
            "obtainWorkEmailPlaceHolder": "输入校园/工作邮箱",
            "informationResult": "已有23人完善信息"  # todo next
        }

    def updateMyselfInfo(self, opType, valueIndex):
        updateParams = self.matchHelper.getUpdateParams(opType, valueIndex)
        if updateParams:
            UserModel.updateByPassportId(self.dbSession, self.passportId, **updateParams)
            # todo next
            self.reloadMatchHelper()
        return self.getMyselfInfo()

    def checkBeforeUpdate(self, opType, valueIndex):
        if opType == const.MODEL_USER_OP_TYPE_SEX and \
                self.userInfo.sex != const.MODEL_USER_SEX_CHOICE_LIST[const.MODEL_USER_DEFAULT_SEX_INDEX] and\
                self.userInfo.sex != const.MODEL_USER_SEX_CHOICE_LIST[int(valueIndex)]:
            return const.RESP_SEX_CANOT_EDIT
        # todo 其他修改限制半年一次修改机会
