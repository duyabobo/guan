#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.myself_helper import UserHelper
from model.user import UserModel
from model.verify import VerifyModel
from ral import user
from service import BaseService
from util.class_helper import lazy_property
from util.const.match import MODEL_WORK_VERIFY_STATUS_YES, OP_TYPE_SEX, SEX_CHOICE_LIST, \
    DEFAULT_SEX_INDEX
from util.const.response import RESP_SEX_CANOT_EDIT


class UserInfoService(BaseService):

    def __init__(self, redis, currentPassport):
        self.redis = redis
        self.currentPassport = currentPassport
        self.passportId = currentPassport.get('id', 0)
        self.userHelper = UserHelper(self.userInfo)
        super(UserInfoService, self).__init__(redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.passportId)

    @property
    def infoFinishCnt(self):
        # 已完成信息完善的用户数量
        return user.getFillFinishCnt(self.redis)

    @property
    def verify(self):
        return VerifyModel.getByPassportId(self.passportId)

    @property
    def isVerified(self):
        return self.verify.work_verify_status == MODEL_WORK_VERIFY_STATUS_YES

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
            "value": "已认证" if self.verify.work_verify_status == MODEL_WORK_VERIFY_STATUS_YES else "未认证",
        }

    def getPhone(self):
        return {
            "desc": "手机认证",
            "value": "已认证" if self.currentPassport.get('phone', '') else "未认证",
        }

    def reloaduserHelper(self):
        userInfo = UserModel.getByPassportId(self.passportId)
        self.userHelper = UserHelper(userInfo)

    def getMyselfInfo(self):
        informationList = self.userHelper.getInformationList()
        columnChangeTypeIndexMap = {v.bindColumnChange: i for i, v in enumerate(informationList)}
        return {
            "informationList": informationList,
            "columnChangeTypeIndexMap": columnChangeTypeIndexMap,  # 给informationList的每个元素一个对应序号
            "workVerify": self.getWork(),
            "obtainWorkEmailPlaceHolder": "输入校园/工作邮箱",
            "informationResult": "已有%s人完善信息" % self.infoFinishCnt,
        }

    def updateMyselfInfo(self, opType, valueIndex):
        updateParams = self.userHelper.getUpdateParams(opType, valueIndex)
        if updateParams:
            UserModel.updateByPassportId(self.passportId, **updateParams)
            # todo next
            self.reloaduserHelper()
            if self.userHelper.hasFillFinish:
                user.addFillFinishSet(self.redis, self.passportId)
        return self.getMyselfInfo()

    def checkBeforeUpdate(self, opType, valueIndex):
        if opType == OP_TYPE_SEX and \
                self.userInfo.sex != SEX_CHOICE_LIST[DEFAULT_SEX_INDEX] and\
                self.userInfo.sex != SEX_CHOICE_LIST[int(valueIndex)]:
            return RESP_SEX_CANOT_EDIT
        # todo 其他修改限制半年一次修改机会
