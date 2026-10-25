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
from service.common.notice_due import NoticeJob
from service.common.page_copy import guan_info_copy
from service.common.meet_outcome import apply_synced_result, record_my_fit, settle_due_meets
from service.common.profile_board import ProfileBoardService
from service.common.profile_match import ProfileMatchService, other_passport_id
from service.meet_notice import MeetNoticeService, page_subscribe
from service.phone_bind import PhoneBindService
from util.class_helper import lazy_property
from util.const import match
from util.const.base import (
    GUAN_INFO_OP_TYPE_QUIT, GUAN_INFO_OP_TYPE_JOIN, GUAN_INFO_OP_TYPE_INVITE,
    MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE,
)
from util.const.notice import SCENE_CANCELLED, SCENE_JOINED, SCENE_UNFIT
from util.const.match import (
    MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX,
    MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_EMPTY,
    MODEL_ACTIVITY_STATE_INVITE_SUCCESS
)
from util.const.mini_program import MYREQUIREMENT_PAGE, MYINFORMATION_PAGE_WITH_ERRMSG
from util.const.progress import (
    HOLD_APPOINTMENT, HOLD_FIT, OP_CHOOSE_FIT, OP_TOWARD_MEET,
    PROGRESS_DESC, PROGRESS_NOT_SELECTED, build_meet_share_guide,
    calc_activity_progress, fit_marks_only_self, get_bottom_buttons, hold_block_reason,
    meet_choice_ready, quit_is_allowed, relationship_hold, result_change_allowed,
)
from util.const.response import (
    RESP_OK, RESP_JOIN_ACTIVITY_FAILED, RESP_HAS_APPOINTMENT, RESP_HAS_FIT_PARTNER,
    RESP_NEED_FILL_INFO, RESP_HAS_TIME_CONFLICT,
    RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI, RESP_MEET_RESULT_ERR,
)

logger = logging.getLogger(__name__)

_SEAT_OPS = (GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN)


class _OperateResult(object):
    def __init__(self, msg, notices=None):
        self.msg = msg
        self.notices = notices or []


class GuanInfoService(BaseService):

    def __init__(self, activityId, passport):
        self.activityId = activityId
        self.passport = passport
        self.passportId = passport.get('id', 0)
        self.activityRecord = None
        self.myInformationPage = MYINFORMATION_PAGE_WITH_ERRMSG
        settle_due_meets(self.passportId)
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
        ready = meet_choice_ready(self.activityRecord) if self.activityRecord else False
        return get_bottom_buttons(self.progressStatus, self.opType, ready, self._my_meet_result())

    def _my_meet_result(self):
        record = self.activityRecord
        if not record:
            return 0
        if self.passportId == record.boy_passport_id:
            return record.boy_meet_result or 0
        if self.passportId == record.girl_passport_id:
            return record.girl_meet_result or 0
        return 0

    def updateMeetResult(self, meetResultValue):
        """合适和恢复关系只记自己。不合适、结束关系同步双方，并用小程序订阅通知对方。"""
        written = self._locked_meet_result(meetResultValue)
        if not isinstance(written, _OperateResult):
            return written
        MeetNoticeService.dispatch(written.notices, record_sent=False)
        return written.msg

    @lock("activityOprete:{activityId}", failRet=RESP_MEET_RESULT_ERR)
    def _locked_meet_result(self, meetResultValue):
        self.reloadActivityRecord()
        if not self.activityRecord or not self._is_activity_participant(self.passportId):
            return RESP_MEET_RESULT_ERR
        ready = meet_choice_ready(self.activityRecord)
        if not result_change_allowed(self.progressStatus, meetResultValue, ready):
            logger.info(
                "meet result rejected activity=%s passport=%s value=%s progress=%s ready=%s",
                self.activityId, self.passportId, meetResultValue, self.progressStatus, ready,
            )
            return RESP_MEET_RESULT_ERR
        if meetResultValue == MODEL_MEET_RESULT_FIT_CHOICE:
            blocked = self._hold_response(OP_CHOOSE_FIT)
            if blocked:
                return blocked
        notices = []
        if fit_marks_only_self(self.progressStatus, meetResultValue):
            record_my_fit(self.activityRecord, self.passportId)
        else:
            apply_synced_result(self.activityRecord, self.passportId, meetResultValue)
            notices = _unfit_notice(self.activityRecord, self.passportId, meetResultValue)
        self.reloadActivityRecord()
        return _OperateResult(RESP_OK, notices)

    def getGuanInfo(self):
        progress = self.progressStatus
        return self._build_page(progress, self.oppositePassportId, self.bottomButtons, viewer=False)

    def getViewerGuanInfo(self, share_openid):
        """亲友从分享打开：只看时间地点，不返回对方资料，也不能操作。"""
        sharer_id = self._sharer_passport_id(share_openid)
        if not self._is_activity_participant(sharer_id):
            logger.info("viewer rejected activityId=%s sharerId=%s", self.activityId, sharer_id)
            return self._build_page(PROGRESS_NOT_SELECTED, 0, [], viewer=True)
        progress = calc_activity_progress(sharer_id, self.activityRecord)
        logger.info(
            "viewer open activityId=%s sharerId=%s progress=%s 不返回对方资料",
            self.activityId, sharer_id, progress,
        )
        return self._build_page(progress, 0, [], viewer=True)

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

    def _build_page(self, progress, opposite_passport_id, bottom_buttons, viewer):
        copy = guan_info_copy()
        rows = [] if viewer else self._opposite_rows(opposite_passport_id)
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
            "subscribe": page_subscribe(viewer),
            "phoneBound": PhoneBindService().bound(self.passportId),
        }

    def _opposite_rows(self, opposite_passport_id):
        if not opposite_passport_id:
            return []
        return ProfileBoardService.rows_for(opposite_passport_id, show_all=False)

    def reloadActivityRecord(self):
        self.activityRecord = ActivityModel.getById(self.activityId, status=match.MODEL_STATUS_YES)

    def _hold_response(self, op):
        """别的场次已经占着约见面、半心或全心时，拦住对应的后续操作。"""
        activities = ActivityModel.getUserAllActivities(self.passportId)
        has_appointment = False
        has_fit = False
        for activity in activities:
            if activity.id == self.activityId:
                continue
            hold = relationship_hold(self.passportId, activity)
            if hold == HOLD_APPOINTMENT:
                has_appointment = True
            elif hold == HOLD_FIT:
                has_fit = True
        reason = hold_block_reason(op, has_appointment, has_fit)
        logger.info(
            "relationship hold passport=%s activity=%s op=%s appointment=%s fit=%s reason=%s",
            self.passportId, self.activityId, op, has_appointment, has_fit, reason or "none",
        )
        if reason == HOLD_FIT:
            return RESP_HAS_FIT_PARTNER
        if reason == HOLD_APPOINTMENT:
            return RESP_HAS_APPOINTMENT
        return None

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

    def _booked_by_other(self, opType):
        """双方已约上之后，见面开始前本人仍可取消。其余操作按场次已被占处理。"""
        if opType == GUAN_INFO_OP_TYPE_QUIT:
            ready = meet_choice_ready(self.activityRecord)
            return not quit_is_allowed(self.progressStatus, ready)
        return self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS

    def _operate_block(self, op_type):
        self.reloadActivityRecord()
        if not self.activityRecord:
            return RESP_JOIN_ACTIVITY_FAILED
        if getattr(self.activityRecord, 'seat_locked', False) and not self._is_activity_participant(self.passportId):
            logger.info("座位解不开，拒绝操作 activity=%s passport=%s", self.activityId, self.passportId)
            return RESP_JOIN_ACTIVITY_FAILED
        if not ProfileBoardService.info_is_filled(self.passportId):
            return RESP_NEED_FILL_INFO
        if self._booked_by_other(op_type):
            logger.info(
                "activity operate rejected activity=%s passport=%s op=%s state=%s progress=%s",
                self.activityId, self.passportId, op_type,
                self.activityRecord.state, self.progressStatus,
            )
            return RESP_JOIN_ACTIVITY_FAILED
        if op_type != self.opType:
            return RESP_JOIN_ACTIVITY_FAILED
        if op_type in _SEAT_OPS:
            blocked = self._hold_response(OP_TOWARD_MEET)
            if blocked:
                return blocked
        if self.opType == GUAN_INFO_OP_TYPE_JOIN and not self._can_join():
            return RESP_JOIN_ACTIVITY_FAILED
        if op_type in _SEAT_OPS and self.timeIsConflict():
            return RESP_HAS_TIME_CONFLICT
        return None

    def activityOprete(self, op_type):
        """邀请、加入、取消。写座位在锁里面。"""
        block = self._operate_block(op_type)
        if block:
            return block
        written = self._locked_apply(op_type)
        if not isinstance(written, _OperateResult):
            return written
        MeetNoticeService.dispatch(written.notices, record_sent=False)
        return written.msg

    @lock("activityOprete:{activityId}", failRet=RESP_JOIN_ACTIVITY_FAILED)
    def _locked_apply(self, op_type):
        block = self._operate_block(op_type)
        if block:
            return block
        was_agreed = self.activityRecord.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS
        partner_id = other_passport_id(self.activityRecord, self.passportId)
        start_time = self.activityRecord.start_time
        update_params, where_params = self.parseUpdataParams(op_type, self.sexIndex)
        updated = ActivityModel.updateById(self.activityId, *where_params, **update_params)
        if not updated:
            logger.info(
                "座位没写上 activity=%s passport=%s op=%s",
                self.activityId, self.passportId, op_type,
            )
            return RESP_JOIN_ACTIVITY_FAILED
        ActivityChangeRecordModel.addOne(self.activityId, self.passportId, op_type)
        self.reloadActivityRecord()
        msg, notices = self._after_seat(op_type, was_agreed, partner_id, start_time)
        return _OperateResult(msg, notices)

    def _after_seat(self, op_type, was_agreed, partner_id, start_time):
        if op_type == GUAN_INFO_OP_TYPE_QUIT:
            notices = []
            if was_agreed and partner_id and start_time:
                notices.append(NoticeJob(partner_id, SCENE_CANCELLED, self.activityId, start_time))
            return RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI, notices
        notices = []
        if op_type == GUAN_INFO_OP_TYPE_JOIN and partner_id and start_time:
            notices.append(NoticeJob(partner_id, SCENE_JOINED, self.activityId, start_time))
        return RESP_OK, notices


def _unfit_notice(activity, actor_passport_id, meet_result_value):
    if meet_result_value < MODEL_MEET_RESULT_UNFIT_CHOICE or not activity or not activity.start_time:
        return []
    partner_id = other_passport_id(activity, actor_passport_id)
    if not partner_id:
        logger.info("不合适提醒未发 activity=%s 没有对方", activity.id)
        return []
    return [NoticeJob(partner_id, SCENE_UNFIT, activity.id, activity.start_time)]
