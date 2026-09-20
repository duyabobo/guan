#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.activity import ActivityModel
from model.activity_change_record import ActivityChangeRecordModel
from model.address import AddressModel
from model.requirement import RequirementModel, UNREACHABLE_REQUIREMENT
from model.user import UserModel
from ral.activity import changeByRequirement
from ral.cache import lock
from service import BaseService
from service.common.guan_helper import GuanHelper
from service.common.match import MatchHelper
from service.common.myself_helper import UserHelper
from service.common.requirement_helper import RequirementHelper
from service.myself import UserInfoService
from util.class_helper import lazy_property
from util.const import match
from util.const.base import (
    GUAN_INFO_OP_TYPE_QUIT, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_INVITE,
    MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE
)
from util.const.match import (
    MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX,
    MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_EMPTY,
    MODEL_ACTIVITY_STATE_INVITE_SUCCESS
)
from util.const.mini_program import MYREQUIREMENT_PAGE, MYINFORMATION_PAGE_WITH_ERRMSG
from util.const.progress import (
    PROGRESS_DESC, calc_activity_progress, get_bottom_buttons
)
from util.const.response import (
    RESP_OK, RESP_JOIN_ACTIVITY_FAILED, RESP_HAS_ONGOING_ACTIVITY,
    RESP_NEED_FILL_INFO, RESP_HAS_TIME_CONFLICT,
    RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI, RESP_MEET_RESULT_ERR
)

logger = logging.getLogger(__name__)


class GuanInfoService(BaseService):

    def __init__(self, activityId, passport):
        self.activityId = activityId
        self.passport = passport
        self.passportId = passport.get('id', 0)
        self.activityRecord = None
        self.myInformationPage = MYINFORMATION_PAGE_WITH_ERRMSG
        self.reloadActivityRecord()
        super(GuanInfoService, self).__init__()

    @lazy_property
    def addressRecord(self):
        return AddressModel.getById(self.activityRecord.address_id)

    @lazy_property
    def userRecord(self):
        return UserModel.getByPassportId(passportId=self.passportId)

    @lazy_property
    def oppositeUserRecord(self):
        if not self.userRecord:
            return None
        passportId = (
            self.activityRecord.girl_passport_id
            if self.userRecord.sexIndex == MODEL_SEX_MALE_INDEX
            else self.activityRecord.boy_passport_id
        )
        return UserModel.getByPassportId(passportId=passportId)

    @lazy_property
    def oppositeRequirementRecord(self):
        if not self.oppositeUserRecord:
            return None
        return RequirementModel.getByPassportId(self.oppositeUserRecord.passport_id)

    @property
    def address(self):
        return self.addressRecord.name

    @property
    def time(self):
        return self.activityRecord.startTimeStr

    @property
    def progressStatus(self):
        """计算用户在当前活动中的进展状态（委托纯函数）"""
        return calc_activity_progress(self.passportId, self.activityRecord)

    @property
    def opType(self):
        """当前活动操作类型（邀请/加入/退出）"""
        if not self.activityRecord.boy_passport_id and not self.activityRecord.girl_passport_id:
            return GUAN_INFO_OP_TYPE_INVITE
        if self.passportId in [self.activityRecord.girl_passport_id, self.activityRecord.boy_passport_id]:
            return GUAN_INFO_OP_TYPE_QUIT
        return GUAN_INFO_OP_TYPE_JOIN

    @property
    def bottomButtons(self):
        """根据进展状态返回底部按钮配置（委托纯函数）"""
        return get_bottom_buttons(self.progressStatus, self.opType)

    @property
    def oppositeInfoDataPairs(self):
        """对方的条件（用户信息），按对列展示"""
        if not self.oppositeUserRecord:
            return []
        uh = UserHelper(self.oppositeUserRecord)
        informationList = uh.getInformationList(checkDynamicData=False)
        opTypeMapInformation = {i.bindChange: i for i in informationList}
        pairs = []
        for opTypes in uh.getInformationPariList():
            pair = []
            for opType in opTypes:
                if opType not in opTypeMapInformation:
                    continue
                info = opTypeMapInformation[opType]
                pair.append({"desc": info.desc, "subDesc": info.subDesc, "value": info.fullValue})
            pairs.append(pair)
        return pairs

    @property
    def oppositeRequirementDataPairs(self):
        """对方的期望（择偶条件），按对列展示"""
        if not self.oppositeRequirementRecord:
            return []
        rh = RequirementHelper(self.oppositeRequirementRecord)
        requirementList = rh.getRequirementList(checkDynamicData=False)
        return [[{"desc": r.desc, "subDesc": r.subDesc, "value": r.fullValue}] for r in requirementList]

    def updateMeetResult(self, meetResultValue):
        """更新见面结果（含合适/不合适/结束/恢复）"""
        if self.passportId == self.activityRecord.boy_passport_id:
            ActivityModel.updateBoyMeetResult(self.activityId, meetResultValue)
        elif self.passportId == self.activityRecord.girl_passport_id:
            ActivityModel.updateGirlMeetResult(self.activityId, meetResultValue)
        else:
            return RESP_MEET_RESULT_ERR
        logger.info("meet_result updated: activityId=%s passportId=%s value=%s",
                    self.activityId, self.passportId, meetResultValue)
        return RESP_OK

    def getGuanInfo(self):
        progress = self.progressStatus
        return {
            "guanId": self.activityId,
            "progressStatus": progress,
            "progressDesc": PROGRESS_DESC.get(progress, ""),
            "activity": {
                "img": GuanHelper.getActivityImg(
                    self.activityRecord, self.addressRecord,
                    self.oppositeUserRecord, self.userRecord, False
                ),
                "time": self.time,
                "address": self.address,
            },
            "opposite": {
                "infoDataPairs": self.oppositeInfoDataPairs,
                "requirementDataPairs": self.oppositeRequirementDataPairs,
            },
            "operate": {
                "bottomButtons": self.bottomButtons,
                "matchConfigPage": MYREQUIREMENT_PAGE,
                "myInformationPage": self.myInformationPage,
                "requirementResult": "%d人将收到邀请" % UserModel.getMatchCnt(passportId=self.passportId),
            },
        }

    def reloadActivityRecord(self):
        self.activityRecord = ActivityModel.getById(self.activityId, status=match.MODEL_STATUS_YES)

    @property
    def hasOngoingActivity(self):
        return bool(ActivityModel.getOngoingActivity(self.passportId))

    def getRequirement(self):
        if self.opType == GUAN_INFO_OP_TYPE_INVITE:
            return None
        elif self.opType == GUAN_INFO_OP_TYPE_JOIN:
            if self.userRecord.sex == MODEL_SEX_MALE_INDEX and self.activityRecord.boy_passport_id != 0:
                return UNREACHABLE_REQUIREMENT
            if self.userRecord.sex == MODEL_SEX_FEMALE_INDEX and self.activityRecord.girl_passport_id != 0:
                return UNREACHABLE_REQUIREMENT
            invitePid = (
                self.activityRecord.girl_passport_id
                if self.userRecord.sex == MODEL_SEX_MALE_INDEX
                else self.activityRecord.boy_passport_id
            )
            if not invitePid:
                return UNREACHABLE_REQUIREMENT
            return RequirementModel.getByPassportId(invitePid)
        elif self.opType == GUAN_INFO_OP_TYPE_QUIT:
            if self.activityRecord.boy_passport_id != 0 and self.activityRecord.girl_passport_id != 0:
                return UNREACHABLE_REQUIREMENT
            invitePid = 0
            if self.userRecord.sex == MODEL_SEX_MALE_INDEX:
                invitePid = self.activityRecord.boy_passport_id or self.activityRecord.girl_passport_id
            elif self.userRecord.sex == MODEL_SEX_FEMALE_INDEX:
                invitePid = self.activityRecord.girl_passport_id or self.activityRecord.boy_passport_id
            if not invitePid:
                return UNREACHABLE_REQUIREMENT
            return RequirementModel.getByPassportId(invitePid)
        return UNREACHABLE_REQUIREMENT

    def parseUpdataParams(self, opType, sexIndex):
        updateParams = {}
        whereParams = []
        if opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN]:
            passportId = self.passportId
            if self.activityRecord.state == MODEL_ACTIVITY_STATE_EMPTY:
                updateParams['state'] = MODEL_ACTIVITY_STATE_INVITING
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_EMPTY)
            elif self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITING:
                updateParams['state'] = MODEL_ACTIVITY_STATE_INVITE_SUCCESS
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_INVITING)
        else:
            passportId = 0
            if self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITING:
                updateParams['state'] = MODEL_ACTIVITY_STATE_EMPTY
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_INVITING)
            elif self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
                updateParams['state'] = MODEL_ACTIVITY_STATE_INVITING
                whereParams.append(ActivityModel.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS)
        if sexIndex == MODEL_SEX_MALE_INDEX:
            updateParams['boy_passport_id'] = passportId
        elif sexIndex == MODEL_SEX_FEMALE_INDEX:
            updateParams['girl_passport_id'] = passportId
        return updateParams, whereParams

    def updateMyInformationPage(self, ret):
        if ret['code'] == RESP_NEED_FILL_INFO['code']:
            self.myInformationPage = self.myInformationPage + ret['errMsg']

    def timeIsConflict(self):
        return bool(ActivityModel.getConflictActivity(self.passportId, self.activityRecord.start_time))

    @lock("activityOprete:{activityId}", failRet=RESP_JOIN_ACTIVITY_FAILED)
    def activityOprete(self, opType):
        """对活动进行操作（邀请/加入/退出）"""
        uis = UserInfoService(self.passport)
        needFilled = uis.userInfoNeedFilled()
        if needFilled:
            return needFilled
        if self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
            return RESP_JOIN_ACTIVITY_FAILED
        if opType != self.opType:
            return RESP_JOIN_ACTIVITY_FAILED
        if self.hasOngoingActivity and opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN]:
            return RESP_HAS_ONGOING_ACTIVITY
        requirement = self.getRequirement()
        if self.opType == GUAN_INFO_OP_TYPE_JOIN and not MatchHelper.match(self.userRecord, requirement):
            return RESP_JOIN_ACTIVITY_FAILED
        if opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN] and self.timeIsConflict():
            return RESP_HAS_TIME_CONFLICT
        updateParams, whereParams = self.parseUpdataParams(opType, uis.userInfo.sexIndex)
        ret = ActivityModel.updateById(self.activityId, *whereParams, **updateParams)
        if not ret:
            return RESP_JOIN_ACTIVITY_FAILED
        ActivityChangeRecordModel.addOne(self.activityId, self.passportId, opType)
        self.reloadActivityRecord()
        changeByRequirement(self.activityRecord.id, requirement, self.getRequirement())
        if opType == GUAN_INFO_OP_TYPE_QUIT:
            return RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI
        return RESP_OK
