#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
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
    girl_passport_id = Column(Integer, default=0)  # 女孩passport_id
    boy_passport_id = Column(Integer, default=0)  # 男孩passport_id
    meet_result = Column(Integer, default=0)  # 见面结果描述文案: MODEL_MEET_RESULT_MAP
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
        return datetime2str(self.start_time, fmt="%Y-%m-%d %H:%M")

    @property
    def boyImg(self):
        return const.CDN_QINIU_BOY_HEAD_IMG  # todo 如果是有男孩参加，就点亮头像，否则是置灰头像

    @property
    def girlImg(self):
        return const.CDN_QINIU_GIRL_HEAD_IMG  # todo 如果是有女孩参加，就点亮头像，否则是置灰头像

    @classmethod
    def updateById(cls, dbSession, activityId, **updateParams):
        dbSession.query(cls).filter(cls.id == activityId).update(updateParams)
        dbSession.flush()

    @classmethod
    def getOngoingActivity(cls, dbSession, passportId):
        return dbSession.query(cls).filter(
            or_(cls.boy_passport_id == passportId, cls.girl_passport_id == passportId)
        ).filter(
            cls.start_time > datetime.datetime.now()
        ).first()

    @classmethod
    def getLastFreeActivity(cls, dbSession):
        return dbSession.query(cls).filter(
            cls.start_time > datetime.datetime.now(),
            cls.girl_passport_id == 0,
            cls.boy_passport_id == 0,
            cls.status == const.MODEL_STATUS_YES
        ).order_by(cls.id.desc()).first()

    @classmethod
    def getLastActivity(cls, dbSession):
        return dbSession.query(cls).filter(
            cls.start_time > datetime.datetime.now(),
            cls.status == const.MODEL_STATUS_YES
        ).order_by(cls.id.desc()).first()

    @classmethod
    def addOne(cls, dbSession, addressId, startTime):
        record = cls(
            address_id=addressId,
            start_time=startTime
        )
        dbSession.add(record)
        dbSession.commit()
        return record
