#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.requirement_helper import RequirementHelper
from model.requirement import RequirementModel
from model.user import UserModel
from service import BaseService
from util.class_helper import lazy_property
from util.const.match import OP_TYPE_SEX, SEX_CHOICE_LIST, DEFAULT_SEX_INDEX
from util.const.response import RESP_USER_SEX_FIRST_EDIT, RESP_REQUIREMENT_SEX_ERROR


class RequirementService(BaseService):

    def __init__(self, redis, passportId):
        self.redis = redis
        self.passportId = passportId
        self.requirementHelper = RequirementHelper(self.requirementInfo)
        super(RequirementService, self).__init__(redis)

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(self.passportId)

    @lazy_property
    def requirementInfo(self):
        return RequirementModel.getByPassportId(self.passportId)

    def reloadMatchHelper(self):
        requirementInfo = RequirementModel.getByPassportId(self.passportId)
        self.requirementHelper = RequirementHelper(requirementInfo)

    def getRequirementInfo(self):
        requirementList = self.requirementHelper.getRequirementList()
        columnChangeTypeIndexMap = {v.bindColumnChange: i for i, v in enumerate(requirementList)}
        return {
            "requirementList": requirementList,
            "columnChangeTypeIndexMap": columnChangeTypeIndexMap,  # 给requirementList的每个元素一个对应序号，用来小程序实时更新对应的picker值
            "requirementResult": "3人满足见面条件"  # todo next
        }

    def updateRequirementInfo(self, opType, valueIndex):
        updateParams = self.requirementHelper.getUpdateParams(opType, valueIndex)
        if updateParams:
            RequirementModel.updateByPassportId(self.passportId, **updateParams)
            self.reloadMatchHelper()
        return self.getRequirementInfo()  # todo 可以扩展需要支持返回成功+提醒的code码

    def checkBeforeUpdate(self, opType, valueIndex):
        if opType == OP_TYPE_SEX and self.userInfo.sex == SEX_CHOICE_LIST[DEFAULT_SEX_INDEX]:
            return RESP_USER_SEX_FIRST_EDIT
        if opType == OP_TYPE_SEX and int(valueIndex) == SEX_CHOICE_LIST.index(self.userInfo.sex):
            return RESP_REQUIREMENT_SEX_ERROR
        # todo 其他修改限制半年一次修改机会
