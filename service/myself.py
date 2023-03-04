#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.myself_helper import UserHelper
from model.requirement import RequirementModel
from model.user import UserModel
from ral import user
from ral.cache import checkCache, deleteCache
from service import BaseService
from util.class_helper import lazy_property
from util.const.match import MODEL_MAIL_TYPE_SCHOOL, MODEL_MAIL_TYPE_WORK, OP_TYPE_MARTIAL_STATUS_PERIOD, \
    DEFAULT_MARTIAL_STATUS_INDEX, MODEL_MARTIAL_STATUS_UNKNOWN, MODEL_STATUS_NO, MODEL_MAIL_TYPE_UNKNOWN
from util.const.match import OP_TYPE_SEX, DEFAULT_SEX_INDEX, OP_TYPE_VERIFY
from util.const.response import RESP_NEED_VERIFY, RESP_NEED_FILL_SEX, RESP_NEED_FILL_BIRTH_YEAR, RESP_NEED_FILL_HEIGHT, \
    RESP_NEED_FILL_WEIGHT, RESP_NEED_FILL_MARTIAL_STATUS, RESP_NEED_FILL_EDUCATION_LEVEL, RESP_NEED_FILL_MONEY_PAY
from util.const.response import RESP_SEX_CANOT_EDIT, RESP_MARTIAL_STATUS_CANOT_EDIT

DEFAULT_VERIFY_TYPE = "未认证"
EDUCATION_VERIFY_TYPE = "教育认证"
WORK_VERIFY_TYPE = "工作认证"
VERIFY_TYPE_DICT = {
    MODEL_MAIL_TYPE_SCHOOL: EDUCATION_VERIFY_TYPE,
    MODEL_MAIL_TYPE_WORK: WORK_VERIFY_TYPE
}


class UserInfoService(BaseService):

    def __init__(self, currentPassport):
        self.currentPassport = currentPassport
        self.passportId = currentPassport.get('id', 0)
        self.userHelper = UserHelper(self.userInfo)
        super(UserInfoService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    @property
    def infoFinishCnt(self):
        # 已完成信息完善的用户数量
        return UserModel.getFillFinishCnt()

    @property
    def isVerified(self):
        return self.userInfo.verify_type != MODEL_MAIL_TYPE_UNKNOWN
    
    @property
    def verifyType(self):
        return VERIFY_TYPE_DICT.get(self.userInfo.verify_type, DEFAULT_VERIFY_TYPE)

    @property
    def infoIsFilled(self):
        if self.verifyType == EDUCATION_VERIFY_TYPE:
            return self.userInfo.sex and self.userInfo.birth_year \
                   and self.userInfo.martial_status and self.userInfo.height and self.userInfo.weight \
                   and self.userInfo.education and self.userInfo.study_region and self.userInfo.education_level
        elif self.verifyType == WORK_VERIFY_TYPE:
            return self.userInfo.sex and self.userInfo.birth_year \
                   and self.userInfo.martial_status and self.userInfo.height and self.userInfo.weight \
                   and self.userInfo.work_region and self.userInfo.work
        else:
            return False

    def userInfoNeedFilled(self):
        # 返回细化提示信息
        if not self.isVerified:
            return RESP_NEED_VERIFY
        elif not self.userInfo.sex:
            return RESP_NEED_FILL_SEX
        elif not self.userInfo.birth_year:
            return RESP_NEED_FILL_BIRTH_YEAR
        elif not self.userInfo.height:
            return RESP_NEED_FILL_HEIGHT
        elif not self.userInfo.weight:
            return RESP_NEED_FILL_WEIGHT
        elif not self.userInfo.education_level:
            return RESP_NEED_FILL_EDUCATION_LEVEL
        elif self.userInfo.verify_type == MODEL_MAIL_TYPE_SCHOOL:  # 学校认证
            pass
        elif self.userInfo.verify_type == MODEL_MAIL_TYPE_WORK:  # 工作认证
            if not self.userInfo.month_pay:
                return RESP_NEED_FILL_MONEY_PAY
        elif self.userInfo.martial_status == MODEL_MARTIAL_STATUS_UNKNOWN:
            return RESP_NEED_FILL_MARTIAL_STATUS
        else:
            return None

    def getVerify(self): 
        return {
            "desc": "认证",
            "value": self.verifyType,
        }

    def getPhone(self):
        return {
            "desc": "手机认证",
            "value": "已认证" if self.currentPassport.get('phone', '') else "未认证",
        }

    def reloaduserHelper(self):
        userInfo = UserModel.getByPassportId(passportId=self.passportId)
        self.userHelper = UserHelper(userInfo)

    @checkCache("UserInfoService:{passportId}")
    def getMyselfInfo(self, checkDynamicData=False):
        _informationList = self.userHelper.getInformationList(checkDynamicData)
        # 认证这里要pop掉，使用workVerify单独去页面展示
        informationList = []
        for i in _informationList:
            if i.bindChange == OP_TYPE_VERIFY:
                continue
            informationList.append(i)
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
        userUpdateParams, requirementUpdateParams = self.userHelper.getUpdateParams(opType, value, column)
        if userUpdateParams:
            checkDynamicData = False
            if not self.userInfoNeedFilled():
                userUpdateParams['info_has_filled'] = 1
                user.addFillFinishSet(self.passportId)
            else:
                userUpdateParams['info_has_filled'] = 0
                user.delFillFinishSet(self.passportId)
            UserModel.updateByPassportId(passportId=self.passportId, **userUpdateParams)
            self.autoFillRequirement(**requirementUpdateParams)  # 自动填充期望信息，只会首次填写某个用户信息时才会自动填充期望，后续更新用户信息，不会更新期望
            self.reloaduserHelper()
        return self.getMyselfInfo(checkDynamicData)

    @deleteCache(["RequirementService:{passportId}"])
    def autoFillRequirement(self, **requirementUpdateParams):
        if requirementUpdateParams:
            RequirementModel.updateByPassportId(self.passportId, **requirementUpdateParams)
            UserModel.getMatchCnt(passportId=self.passportId, forceRefreshCache=True)

    def checkBeforeUpdate(self, opType, value):
        if opType == OP_TYPE_SEX and \
                self.userInfo.sex != DEFAULT_SEX_INDEX and self.userInfo.sex != value:
            return RESP_SEX_CANOT_EDIT
        if opType == OP_TYPE_MARTIAL_STATUS_PERIOD and self.userInfo.martial_status != DEFAULT_MARTIAL_STATUS_INDEX \
                and value == DEFAULT_MARTIAL_STATUS_INDEX:
            return RESP_MARTIAL_STATUS_CANOT_EDIT
        # todo 其他修改限制，比如一月一次修改工作地址的机会

    @deleteCache(["UserInfoService:{passportId}"])
    def resetHeadImg(self):
        # 重置头像
        UserModel.updateByPassportId(passportId=self.passportId, has_head_img=MODEL_STATUS_NO)
