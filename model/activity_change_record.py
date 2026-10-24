#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.ctx import getDbSession
from util.slot_blind import activity_slot_key

logger = logging.getLogger(__name__)


class ActivityChangeRecordModel(BaseModel):
    """活动变化流水记录"""
    __tablename__ = 'activity_change_record'
    id = Column(Integer, primary_key=True)  # 自增
    activity_id = Column(Integer)  # 不再写入真实场次编号
    slot_key = Column(String, default='')
    passport_id = Column(Integer)  # passport_id
    change_type = Column(Integer)  # 变化类型：0未知，1发出邀请，2接受邀请，3邀请者取消，4接受者取消
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def addOne(cls, activityId, passportId, changeType):
        slot = activity_slot_key(activityId)
        if not slot:
            logger.error("活动流水未记，盲索引为空 activity=%s", activityId)
            return None
        record = cls(
            activity_id=0,
            slot_key=slot,
            passport_id=passportId,
            change_type=changeType,
        )
        getDbSession().add(record)
        getDbSession().flush()
        return record
