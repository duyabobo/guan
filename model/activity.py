#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column, and_
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.sql import or_

from model import BaseModel
from util.const import match
from util.const.base import MODEL_MEET_RESULT_UNKNOWN, MODEL_MEET_RESULT_FIT_CHOICE, MODEL_MEET_RESULT_UNFIT_CHOICE, \
    UNFIX_SHOW_DELAY_DAYS
from util.const.match import MODEL_ACTIVITY_AVALIABLE_STATE_LIST, MODEL_ACTIVITY_STATE_EMPTY, \
    MODEL_ACTIVITY_STATE_INVITE_SUCCESS
from util.ctx import getDbSession
from util.time_cost import timecost
from util.util_time import datetime2hommization


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
    def getConflictActivity(cls, passportId, start_time):
        return getDbSession().query(cls.id).filter(
            or_(
                cls.boy_passport_id == passportId,
                cls.girl_passport_id == passportId
            ),
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
        whereParams = [
            cls.status == match.MODEL_STATUS_YES,
            cls.id.in_(activityIds),
            cls.state.in_(MODEL_ACTIVITY_AVALIABLE_STATE_LIST),
            cls.start_time > datetime.datetime.now()
        ]
        if exceptPassportId:
            whereParams.extend([cls.girl_passport_id != exceptPassportId, cls.boy_passport_id != exceptPassportId])
        return getDbSession().query(cls).filter(*whereParams).\
            order_by(cls.state.desc(), cls.start_time.asc()).all()

    @classmethod
    def getById(cls, activityId, status=None):
        whereParams = [cls.id == activityId]
        if status != None:
            whereParams.append(cls.status == status)
        return getDbSession().query(cls).filter(*whereParams).first()

    @property
    def startTimeStr(self):
        return datetime2hommization(self.start_time)

    @classmethod
    def updateById(cls, activityId, *whereParams, **updateParams):
        ret = getDbSession().query(cls).filter(cls.id == activityId, *whereParams).update(updateParams)
        getDbSession().commit()
        return ret

    @classmethod
    @timecost
    def getOngoingActivity(cls, passportId):
        """参与活动，且关系发展中"""
        if not passportId:
            return None
        return getDbSession().query(cls).filter(
            cls.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
            cls.start_time <= datetime.datetime.now(),
            or_(
                and_(
                    cls.boy_passport_id == passportId,
                    cls.boy_meet_result.in_([MODEL_MEET_RESULT_UNKNOWN, MODEL_MEET_RESULT_FIT_CHOICE]),
                ),
                and_(
                    cls.girl_passport_id == passportId,
                    cls.girl_meet_result.in_([MODEL_MEET_RESULT_UNKNOWN, MODEL_MEET_RESULT_FIT_CHOICE]),
                )
            )
        ).first()

    @classmethod
    def getLastFreeActivity(cls, addressId):
        return getDbSession().query(cls).filter(
            cls.start_time > datetime.datetime.now() + datetime.timedelta(days=14),
            cls.address_id == addressId,
            cls.girl_passport_id == 0,
            cls.boy_passport_id == 0,
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
        """邀请尚未见面的||意向不合适的一周内"""
        if not passportId:
            return []
        unfixShowDelayTime = datetime.datetime.now() + datetime.timedelta(days=UNFIX_SHOW_DELAY_DAYS)
        return getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES,
            or_(
                cls.start_time > datetime.datetime.now(),
                and_(
                    cls.start_time < unfixShowDelayTime,
                    cls.boy_passport_id == passportId,
                    cls.boy_meet_result.not_in_([MODEL_MEET_RESULT_UNKNOWN, MODEL_MEET_RESULT_FIT_CHOICE]),
                ),
                and_(
                    cls.start_time < unfixShowDelayTime,
                    cls.girl_passport_id == passportId,
                    cls.girl_meet_result.not_in_([MODEL_MEET_RESULT_UNKNOWN, MODEL_MEET_RESULT_FIT_CHOICE]),
                )
            )
        ).order_by(cls.state.desc(), cls.start_time.asc()).all()
