#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

from sqlalchemy import Column, and_
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.sql import or_

from model import BaseModel
from util.const import match
from util.const.base import MODEL_MEET_RESULT_UNKNOWN, MODEL_MEET_RESULT_FIT_CHOICE, \
    UNFIX_SHOW_DELAY_DAYS
from util.const.match import (
    MODEL_ACTIVITY_AVALIABLE_STATE_LIST,
    MODEL_ACTIVITY_STATE_EMPTY,
    MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
    MODEL_ACTIVITY_STATE_INVITING,
)
from util.ctx import getDbSession
from util.time_cost import timecost
from util.util_time import datetime2hommization

logger = logging.getLogger(__name__)


class ActivityModel(BaseModel):
    """活动"""
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)  # 自增
    address_id = Column(Integer, default=0)  # 地点id
    start_time = Column(TIMESTAMP, default="1970-01-01")  # 开始时间
    girl_passport_id = Column(Integer, default=0)  # 女孩passport_id
    boy_passport_id = Column(Integer, default=0)  # 男孩passport_id
    state = Column(Integer, default=0)  # 活动状态：MODEL_ACTIVITY_STATE
    girl_meet_result = Column(Integer, default=0)  # 见面结果描述文案: MODEL_MEET_RESULT_MAP
    boy_meet_result = Column(Integer, default=0)  # 见面结果描述文案: MODEL_MEET_RESULT_MAP
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    @timecost
    def updateBoyMeetResult(cls, activityId, meetResultValue):
        getDbSession().query(cls).filter(cls.id == activityId).update({cls.boy_meet_result: meetResultValue})
        getDbSession().commit()

    @classmethod
    @timecost
    def updateGirlMeetResult(cls, activityId, meetResultValue):
        getDbSession().query(cls).filter(cls.id == activityId).update({cls.girl_meet_result: meetResultValue})
        getDbSession().commit()

    @classmethod
    @timecost
    def updateEachMeetResult(cls, activity_id, boy_result, girl_result):
        getDbSession().query(cls).filter(cls.id == activity_id).update({
            cls.boy_meet_result: boy_result,
            cls.girl_meet_result: girl_result,
        }, synchronize_session=False)
        getDbSession().commit()

    @classmethod
    @timecost
    def updateBothMeetResults(cls, activityId, meetResultValue):
        cls.updateBothMeetResultsByIds([activityId], meetResultValue)

    @classmethod
    @timecost
    def updateBothMeetResultsByIds(cls, activity_ids, meetResultValue):
        ids = [activity_id for activity_id in activity_ids if activity_id]
        if not ids:
            return
        getDbSession().query(cls).filter(cls.id.in_(ids)).update({
            cls.boy_meet_result: meetResultValue,
            cls.girl_meet_result: meetResultValue,
        }, synchronize_session=False)
        getDbSession().commit()

    @classmethod
    def list_notice_candidates(cls, now, decide_start, soon_end, expire_end, limit):
        """可能需要到点提醒的场次。窗口由调用方算好，这里只查一次。"""
        rows = getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES,
            or_(
                and_(
                    cls.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
                    cls.boy_meet_result == 0,
                    cls.girl_meet_result == 0,
                    cls.start_time >= decide_start,
                    cls.start_time <= soon_end,
                ),
                and_(
                    cls.state == MODEL_ACTIVITY_STATE_INVITING,
                    cls.start_time > now,
                    cls.start_time <= expire_end,
                ),
            ),
        ).order_by(cls.start_time.asc()).limit(limit).all()
        return _fill(rows)

    @classmethod
    def list_deposit_due(cls, earliest, deadline, limit):
        """已经约上、过了签到时限、还在回溯窗口里的场次。"""
        rows = getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES,
            cls.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            cls.start_time >= earliest,
            cls.start_time <= deadline,
        ).order_by(cls.start_time.asc()).limit(limit).all()
        return _fill(rows)

    @classmethod
    def listUnsetSuccess(cls, passport_id):
        """双方都还没表态、且已经约上的见面。时间是否到期由调用方判断。"""
        activity_ids = _seat_ids(passport_id)
        if not activity_ids:
            return []
        rows = getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES,
            cls.id.in_(activity_ids),
            cls.state == match.MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            cls.boy_meet_result == 0,
            cls.girl_meet_result == 0,
        ).all()
        return _fill(rows)

    @classmethod
    @timecost
    def getConflictActivity(cls, passportId, start_time):
        activity_ids = _seat_ids(passportId)
        if not activity_ids:
            return []
        return getDbSession().query(cls.id).filter(
            cls.id.in_(activity_ids),
            cls.start_time >= start_time.date(),
            cls.start_time <= start_time.date() + datetime.timedelta(days=1)
        ).all()

    @classmethod
    @timecost
    def listActivityIdsByAddressIds(cls, addressIds, state, limit):
        whereParams = [
            cls.status == match.MODEL_STATUS_YES,
            cls.start_time > datetime.datetime.now(),
            cls.state == state
        ]
        if addressIds:
            whereParams.append(cls.address_id.in_(addressIds))
        return getDbSession().query(cls.id, cls.state).filter(*whereParams).limit(limit).all()

    @classmethod
    @timecost
    def listActivity(cls, activityIds, exceptPassportId):
        activity_ids = _without_passport(activityIds, exceptPassportId)
        if not activity_ids:
            return []
        rows = getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES,
            cls.id.in_(activity_ids),
            cls.state.in_(MODEL_ACTIVITY_AVALIABLE_STATE_LIST),
            cls.start_time > datetime.datetime.now()
        ).order_by(cls.state.desc(), cls.start_time.asc()).all()
        return _fill(rows)

    @classmethod
    def getById(cls, activityId, status=None):
        whereParams = [cls.id == activityId]
        if status != None:
            whereParams.append(cls.status == status)
        row = getDbSession().query(cls).filter(*whereParams).first()
        if row:
            _fill([row])
        return row

    @property
    def startTimeStr(self):
        return datetime2hommization(self.start_time)

    @classmethod
    def updateById(cls, activityId, *whereParams, **updateParams):
        from service.meet_seat import apply_seat_changes, take_seat_updates
        seat_changes = take_seat_updates(updateParams)
        session = getDbSession()
        ret = session.query(cls).filter(cls.id == activityId, *whereParams).update(updateParams)
        if ret and seat_changes and not apply_seat_changes(activityId, seat_changes):
            session.rollback()
            logger.error("见面座位没有写上，活动更新已回滚 activity=%s", activityId)
            return 0
        session.commit()
        return ret

    @classmethod
    def getLastFreeActivity(cls, addressId):
        return getDbSession().query(cls).filter(
            cls.start_time > datetime.datetime.now() + datetime.timedelta(days=14),
            cls.address_id == addressId,
            cls.state == MODEL_ACTIVITY_STATE_EMPTY,
            cls.status == match.MODEL_STATUS_YES
        ).order_by(cls.id.desc()).first()

    @classmethod
    def getLastActivity(cls, addressId):
        return getDbSession().query(cls).filter(
            cls.address_id == addressId,
            cls.status == match.MODEL_STATUS_YES
        ).order_by(cls.id.desc()).first()

    @classmethod
    def addOne(cls, addressId, startTime):
        record = cls(
            address_id=addressId,
            start_time=startTime
        )
        getDbSession().add(record)
        getDbSession().commit()
        return record

    @classmethod
    @timecost
    def getUserAllActivities(cls, passportId):
        """获取用户参与的所有活动（不限状态），用于列表页全量展示"""
        activity_ids = _seat_ids(passportId)
        if not activity_ids:
            return []
        rows = getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES,
            cls.id.in_(activity_ids),
        ).order_by(cls.state.desc(), cls.start_time.asc()).all()
        return _fill(rows)

    @classmethod
    def getExpireActivityIds(cls):
        now = datetime.datetime.now()
        oneDayAgo = now - datetime.timedelta(days=1)
        oneDayLater = now + datetime.timedelta(days=1)
        return getDbSession().query(cls.id).filter(
            or_(
                cls.status == match.MODEL_STATUS_NO,
                cls.start_time <= now,
                and_(
                    cls.start_time >= oneDayAgo,
                    cls.start_time <= oneDayLater,
                    cls.state == MODEL_ACTIVITY_STATE_EMPTY
                )
            )
        ).order_by(cls.id.desc())

    @classmethod
    @timecost
    def getUnfinishedActivities(cls, passportId):
        """邀请尚未见面的||尚未表达意向的||意向不合适的一周内"""
        activity_ids = _seat_ids(passportId)
        if not activity_ids:
            return []
        now = datetime.datetime.now()
        delay_end = now + datetime.timedelta(days=UNFIX_SHOW_DELAY_DAYS)
        rows = getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES,
            cls.id.in_(activity_ids),
        ).order_by(cls.state.desc(), cls.start_time.asc()).all()
        kept = [row for row in _fill(rows) if _still_unfinished(row, passportId, now, delay_end)]
        return kept


def _seat_ids(passport_id):
    from service.meet_seat import activity_ids_of
    if not passport_id:
        return []
    return activity_ids_of(passport_id)


def _without_passport(activity_ids, passport_id):
    ids = [activity_id for activity_id in activity_ids or [] if activity_id]
    if not passport_id:
        return ids
    mine = set(_seat_ids(passport_id))
    return [activity_id for activity_id in ids if activity_id not in mine]


def _fill(rows):
    from service.meet_seat import fill_occupants
    rows = list(rows or [])
    fill_occupants(rows)
    return rows


def _still_unfinished(activity, passport_id, now, delay_end):
    if activity.start_time and activity.start_time > now:
        return True
    if not activity.start_time or activity.start_time >= delay_end:
        return False
    past_result = _own_result(activity, passport_id)
    if past_result is None:
        return False
    return past_result not in (MODEL_MEET_RESULT_UNKNOWN, MODEL_MEET_RESULT_FIT_CHOICE)


def _own_result(activity, passport_id):
    if passport_id == activity.boy_passport_id:
        return activity.boy_meet_result
    if passport_id == activity.girl_passport_id:
        return activity.girl_meet_result
    return None
