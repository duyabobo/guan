#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from model.activity import ActivityModel
from model.activity_change_record import ActivityChangeRecordModel
from model.address import AddressModel
from model.passport import PassportModel
from ral.cache import lock
from service import BaseService
from service.common.guan_helper import GuanHelper
from service.common.page_copy import guan_info_copy
from service.common.profile_board import ProfileBoardService
from service.common.profile_match import ProfileMatchService
from util.class_helper import lazy_property
from util.const import match
from util.const.base import (
    GUAN_INFO_OP_TYPE_QUIT, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_INVITE,
)
from util.const.match import (
    MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX,
    MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_EMPTY,
    MODEL_ACTIVITY_STATE_INVITE_SUCCESS
)
from util.const.mini_program import MYREQUIREMENT_PAGE, MYINFORMATION_PAGE_WITH_ERRMSG
from util.const.progress import (
    PROGRESS_DESC, PROGRESS_NOT_SELECTED, build_meet_share_guide,
    calc_activity_progress, get_bottom_buttons,
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
    def sexIndex(self):
        return ProfileBoardService.sex_of(self.passportId)

    @lazy_property
    def oppositePassportId(self):
        if self.sexIndex == MODEL_SEX_MALE_INDEX:
            return self.activityRecord.girl_passport_id
        if self.sexIndex == MODEL_SEX_FEMALE_INDEX:
            return self.activityRecord.boy_passport_id
        return self.activityRecord.girl_passport_id or self.activityRecord.boy_passport_id

    @property
    def address(self):
        if not self.addressRecord:
            return ""
        return self.addressRecord.name or ""

    @property
    def time(self):
        if not self.activityRecord:
            return ""
        return self.activityRecord.startTimeStr or ""

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
        return self._build_page(progress, self.oppositePassportId, self.bottomButtons, viewer=False)

    def getViewerGuanInfo(self, share_openid):
        """好友从分享卡片打开：看到分享人眼中的这一场，但不能操作。"""
        sharer_id = self._sharer_passport_id(share_openid)
        if not self._is_activity_participant(sharer_id):
            logger.info("viewer rejected activityId=%s sharerId=%s", self.activityId, sharer_id)
            return self._build_page(PROGRESS_NOT_SELECTED, 0, [], viewer=True)
        progress = calc_activity_progress(sharer_id, self.activityRecord)
        opposite_id = self._opposite_passport_id(sharer_id)
        logger.info("viewer open activityId=%s sharerId=%s progress=%s",
                    self.activityId, sharer_id, progress)
        return self._build_page(progress, opposite_id, [], viewer=True)

    def _sharer_passport_id(self, share_openid):
        if not share_openid:
            return 0
        sharer = PassportModel.getByOpenid(share_openid)
        if not sharer:
            return 0
        return sharer.id

    def _is_activity_participant(self, passport_id):
        if not passport_id or not self.activityRecord:
            return False
        return passport_id in (self.activityRecord.boy_passport_id, self.activityRecord.girl_passport_id)

    def _opposite_passport_id(self, passport_id):
        sex_index = ProfileBoardService.sex_of(passport_id)
        if sex_index == MODEL_SEX_MALE_INDEX:
            return self.activityRecord.girl_passport_id
        if sex_index == MODEL_SEX_FEMALE_INDEX:
            return self.activityRecord.boy_passport_id
        if passport_id == self.activityRecord.boy_passport_id:
            return self.activityRecord.girl_passport_id
        if passport_id == self.activityRecord.girl_passport_id:
            return self.activityRecord.boy_passport_id
        return 0

    def _build_page(self, progress, opposite_passport_id, bottom_buttons, viewer):
        copy = guan_info_copy()
        rows = ProfileBoardService.rows_for(opposite_passport_id) if opposite_passport_id else []
        return {
            "guanId": self.activityId,
            "progressStatus": progress,
            "progressDesc": PROGRESS_DESC.get(progress, ""),
            "viewer": viewer,
            "copy": copy,
            "activity": {
                "img": GuanHelper.getActivityImg(self.addressRecord, False),
                "time": self.time,
                "address": self.address,
            },
            "opposite": {
                "rows": rows,
            },
            "operate": {
                "bottomButtons": bottom_buttons,
                "matchConfigPage": MYREQUIREMENT_PAGE,
                "myInformationPage": self.myInformationPage,
            },
            "share": build_meet_share_guide(progress, copy["shareLabel"], viewer),
        }

    def reloadActivityRecord(self):
        self.activityRecord = ActivityModel.getById(self.activityId, status=match.MODEL_STATUS_YES)

    @property
    def hasOngoingActivity(self):
        return bool(ActivityModel.getOngoingActivity(self.passportId))

    def _my_slot_taken(self):
        if self.sexIndex == MODEL_SEX_MALE_INDEX:
            return bool(self.activityRecord.boy_passport_id)
        if self.sexIndex == MODEL_SEX_FEMALE_INDEX:
            return bool(self.activityRecord.girl_passport_id)
        return True

    def _can_join(self):
        if self._my_slot_taken() or not self.oppositePassportId:
            return False
        return ProfileMatchService.user_accepts_requirement(self.passportId, self.oppositePassportId)

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
        if not ProfileBoardService.info_is_filled(self.passportId):
            return RESP_NEED_FILL_INFO
        if self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
            return RESP_JOIN_ACTIVITY_FAILED
        if opType != self.opType:
            return RESP_JOIN_ACTIVITY_FAILED
        if self.hasOngoingActivity and opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN]:
            return RESP_HAS_ONGOING_ACTIVITY
        if self.opType == GUAN_INFO_OP_TYPE_JOIN and not self._can_join():
            return RESP_JOIN_ACTIVITY_FAILED
        if opType in [GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN] and self.timeIsConflict():
            return RESP_HAS_TIME_CONFLICT
        updateParams, whereParams = self.parseUpdataParams(opType, self.sexIndex)
        ret = ActivityModel.updateById(self.activityId, *whereParams, **updateParams)
        if not ret:
            return RESP_JOIN_ACTIVITY_FAILED
        ActivityChangeRecordModel.addOne(self.activityId, self.passportId, opType)
        self.reloadActivityRecord()
        if opType == GUAN_INFO_OP_TYPE_QUIT:
            return RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI
        return RESP_OK
