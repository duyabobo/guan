#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.myself_helper import UserHelper
from model.user import UserModel
from model.verify import VerifyModel
from ral import user
from ral.cache import checkCache, deleteCache
from service import BaseService
from util.class_helper import lazy_property
from util.const.match import MODEL_MAIL_TYPE_SCHOOL, MODEL_MAIL_TYPE_WORK, OP_TYPE_MARTIAL_STATUS, \
    DEFAULT_MARTIAL_STATUS_INDEX
from util.const.match import MODEL_MAIL_VERIFY_STATUS_YES, OP_TYPE_SEX, DEFAULT_SEX_INDEX
from util.const.response import RESP_SEX_CANOT_EDIT, RESP_MARTIAL_STATUS_CANOT_EDIT


class UserInfoService(BaseService):

    def __init__(self, currentPassport):
        self.currentPassport = currentPassport
        self.passportId = currentPassport.get('id', 0)
        self.userHelper = UserHelper(self.userInfo)
        super(UserInfoService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.passportId)

    @property
    def infoFinishCnt(self):
        # 已完成信息完善的用户数量
        return UserModel.getFillFinishCnt()

    @property
    def verify(self):
        return VerifyModel.getByPassportId(self.passportId)

    @property
    def isVerified(self):
        return self.verify.mail_verify_status == MODEL_MAIL_VERIFY_STATUS_YES

    @property
    def infoIsFilled(self):
        return self.userInfo.sex and self.userInfo.birth_year \
               and self.userInfo.martial_status and self.userInfo.height \
               and self.userInfo.weight and self.userInfo.education

    @property
    def userInfoIsFilled(self):
        return self.isVerified and self.infoIsFilled

    def getVerify(self):
        verifyType = "未认证"
        if self.verify.mail_verify_status == MODEL_MAIL_VERIFY_STATUS_YES:
            if self.verify.mail_type == MODEL_MAIL_TYPE_SCHOOL:
                verifyType = "教育认证"
            elif self.verify.mail_type == MODEL_MAIL_TYPE_WORK:
                verifyType = "工作认证"
        return {
            "desc": "认证",
            "value": verifyType,
            "is_student": self.verify.mail_type
        }

    def getPhone(self):
        return {
            "desc": "手机认证",
            "value": "已认证" if self.currentPassport.get('phone', '') else "未认证",
        }

    def reloaduserHelper(self):
        userInfo = UserModel.getByPassportId(self.passportId)
        self.userHelper = UserHelper(userInfo)

    @checkCache("UserInfoService:{passportId}")
    def getMyselfInfo(self, checkDynamicData=False):
        informationList = self.userHelper.getInformationList(checkDynamicData)
        columnChangeTypeIndexMap = {v.bindColumnChange: i for i, v in enumerate(informationList)}
        return {
            "informationList": informationList,
            "columnChangeTypeIndexMap": columnChangeTypeIndexMap,  # 给informationList的每个元素一个对应序号
            "workVerify": self.getVerify(),
            "obtainWorkEmailPlaceHolder": "输入您的大学邮箱或工作邮箱",
            "informationResult": "%s人完善个人信息" % self.infoFinishCnt,
        }

    @deleteCache(["UserInfoService:{passportId}"])
    def updateMyselfInfo(self, opType, value, column=None):
        checkDynamicData = True
        updateParams = self.userHelper.getUpdateParams(opType, value, column)
        if updateParams:
            checkDynamicData = False
            if self.userHelper.hasFillFinish:
                updateParams['info_has_filled'] = 1
                user.addFillFinishSet(self.passportId)
            else:
                updateParams['info_has_filled'] = 0
                user.delFillFinishSet(self.passportId)
            UserModel.updateByPassportId(self.passportId, **updateParams)
            self.reloaduserHelper()
        return self.getMyselfInfo(checkDynamicData)

    def checkBeforeUpdate(self, opType, value):
        if opType == OP_TYPE_SEX and \
                self.userInfo.sex != DEFAULT_SEX_INDEX and self.userInfo.sex != value:
            return RESP_SEX_CANOT_EDIT
        if opType == OP_TYPE_MARTIAL_STATUS and self.userInfo.martial_status != DEFAULT_MARTIAL_STATUS_INDEX \
                and value == DEFAULT_MARTIAL_STATUS_INDEX:
            return RESP_MARTIAL_STATUS_CANOT_EDIT
        # todo 其他修改限制，比如一月一次修改工作地址的机会
