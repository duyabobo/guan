#! /usr/bin/env python
# -*- coding: utf-8 -*-
from common.requirement_helper import RequirementHelper
from model.activity import ActivityModel
from model.requirement import RequirementModel
from model.user import UserModel
from ral.activity import changeByRequirement
from ral.cache import checkCache, deleteCache
from service import BaseService
from util.class_helper import lazy_property
from util.const.match import OP_TYPE_SEX, SEX_CHOICE_LIST, DEFAULT_SEX_INDEX
from util.const.response import RESP_USER_SEX_FIRST_EDIT, RESP_REQUIREMENT_SEX_ERROR


class RequirementService(BaseService):

    def __init__(self, passportId):
        self.passportId = passportId
        self.requirementHelper = RequirementHelper(self.requirementInfo)
        super(RequirementService, self).__init__()

    @lazy_property
    def userInfo(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    @lazy_property
    def requirementInfo(self):
        return RequirementModel.getByPassportId(self.passportId)

    def reloadMatchHelper(self):
        requirementInfo = RequirementModel.getByPassportId(self.passportId)
        self.requirementHelper = RequirementHelper(requirementInfo)

    @checkCache("RequirementService:{passportId}")
    def getRequirementInfo(self, checkDynamicData=False):
        """
        checkDynamicData：是否要读取多重选择器用户临时选择的数据
        """
        requirementList = self.requirementHelper.getRequirementList(checkDynamicData)
        columnChangeTypeIndexMap = {v.bindColumnChange: i for i, v in enumerate(requirementList)}
        return {
            "requirementList": requirementList,
            "columnChangeTypeIndexMap": columnChangeTypeIndexMap,  # 给requirementList的每个元素一个对应序号，用来小程序实时更新对应的picker值
            "requirementResult": "%d人满足你的期望" % UserModel.getMatchCnt(self.passportId)
        }

    def updateMatchedActivityId(self, passportId, oldRequirement, newRequirement):
        activityRecord = ActivityModel.getOngoingActivity(passportId)
        if activityRecord:
            changeByRequirement(activityRecord.id, oldRequirement, newRequirement)

    @deleteCache(["RequirementService:{passportId}", "MatchHelper:{passportId}"])
    def updateRequirementInfo(self, opType, value, column=None):
        checkDynamicData = True
        updateParams = self.requirementHelper.getUpdateParams(opType, value, column)
        if updateParams:
            checkDynamicData = False
            RequirementModel.updateByPassportId(self.passportId, **updateParams)
            UserModel.getMatchCnt(self.passportId, forceRefreshCache=True)
            oldRequirement = self.requirementHelper.requirement
            self.reloadMatchHelper()
            # 更新活动id匹配缓存
            self.updateMatchedActivityId(self.passportId, oldRequirement, self.requirementHelper.requirement)
        return self.getRequirementInfo(checkDynamicData)  # todo 可以扩展需要支持返回成功+提醒的code码

    def checkBeforeUpdate(self, opType, value):
        if opType == OP_TYPE_SEX and self.userInfo.sex == SEX_CHOICE_LIST[DEFAULT_SEX_INDEX]:
            return RESP_USER_SEX_FIRST_EDIT
        if opType == OP_TYPE_SEX and value == self.userInfo.sex:
            return RESP_REQUIREMENT_SEX_ERROR
        # todo 其他修改限制半年一次修改机会
