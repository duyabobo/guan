#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.sql import or_

from model import BaseModel
from util.const import match
from util.const.match import MODEL_ACTIVITY_AVALIABLE_STATE_LIST
from util.const.qiniu_img import CDN_QINIU_BOY_HEAD_IMG, CDN_QINIU_GIRL_HEAD_IMG
from util.ctx import getDbSession
from util.util_time import datetime2str


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
    def listByAddressIds(cls, addressIds):
        return getDbSession().query(cls.id, cls.boy_passport_id, cls.girl_passport_id).filter(
            cls.status == match.MODEL_STATUS_YES,
            cls.address_id.in_(addressIds),
            cls.start_time > datetime.datetime.now(),
            cls.state.in_(MODEL_ACTIVITY_AVALIABLE_STATE_LIST)
        )

    @classmethod
    def listActivity(cls, activityIds, limit, exceptPassportId):
        return getDbSession().query(cls).filter(
            cls.status == match.MODEL_STATUS_YES, cls.id.in_(activityIds), cls.state.in_(MODEL_ACTIVITY_AVALIABLE_STATE_LIST),
            cls.girl_passport_id != exceptPassportId, cls.boy_passport_id != exceptPassportId
        ).order_by(cls.state.desc(), cls.start_time.asc()).limit(limit).all()

    @classmethod
    def getById(cls, activityId):
        return getDbSession().query(cls).filter(cls.id == activityId, cls.status == match.MODEL_STATUS_YES).first()

    @property
    def startTimeStr(self):
        return datetime2str(self.start_time, fmt="%Y-%m-%d %H:%M")

    @property
    def boyImg(self):
        return CDN_QINIU_BOY_HEAD_IMG if self.boy_passport_id else ""

    @property
    def girlImg(self):
        return CDN_QINIU_GIRL_HEAD_IMG if self.girl_passport_id else ""

    @classmethod
    def updateById(cls, activityId, *whereParams, **updateParams):
        ret = getDbSession().query(cls).filter(cls.id == activityId, *whereParams).update(updateParams)
        getDbSession().commit()
        return ret

    @classmethod
    def getOngoingActivity(cls, passportId):
        return getDbSession().query(cls).filter(
            or_(cls.boy_passport_id == passportId, cls.girl_passport_id == passportId)
        ).filter(
            cls.start_time > datetime.datetime.now().date()
        ).first()

    @classmethod
    def getLastFreeActivity(cls, addressId):
        return getDbSession().query(cls).filter(
            cls.start_time > datetime.datetime.now(),
            cls.address_id == addressId,
            cls.girl_passport_id == 0,
            cls.boy_passport_id == 0,
            cls.status == match.MODEL_STATUS_YES
        ).order_by(cls.id.desc()).first()

    @classmethod
    def getLastActivity(cls, addressId):
        return getDbSession().query(cls).filter(
            cls.start_time > datetime.datetime.now(),
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
