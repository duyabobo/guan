#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.sql import or_

from model import BaseModel
from util import const
from util.util_time import datetime2str


class ActivityModel(BaseModel):
    """活动"""
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)  # 自增
    address_id = Column(Integer, default=0)  # 地点id
    start_time = Column(TIMESTAMP, default="1970-01-01")  # 开始时间
    invite_passport_id = Column(Integer, default=0)  # 邀请者passport_id
    accept_passport_id = Column(Integer, default=0)  # 接受者passport_id
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def listByAddressIds(cls, dbSession, addressIds):
        return dbSession.query(cls).filter(
            cls.status == const.MODEL_STATUS_YES,
            cls.address_id.in_(addressIds),
            cls.start_time > datetime.datetime.now().date()
        ).all()

    @classmethod
    def getById(cls, dbSession, activityId):
        return dbSession.query(cls).filter(cls.id == activityId, cls.status == const.MODEL_STATUS_YES).first()

    @property
    def startTimeStr(self):
        return datetime2str(self.start_time, fmt="%m-%d %H:%M")

    @classmethod
    def updateById(cls, dbSession, activityId, **updateParams):
        dbSession.query(cls).filter(cls.id == activityId).update(updateParams)
        dbSession.flush()

    @classmethod
    def getOngoingActivity(cls, dbSession, passportId):
        return dbSession.query(cls).filter(
            or_(cls.accept_passport_id == passportId, cls.invite_passport_id == passportId)
        ).filter(
            cls.start_time > datetime.datetime.now()
        ).first()
