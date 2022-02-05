#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel


class ActivityModel(BaseModel):
    """活动"""
    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)  # 自增
    address_id = Column(Integer)  # 地点id
    start_time = Column(TIMESTAMP)  # 开始时间
    invite_uid = Column(Integer)  # 邀请者uid
    accept_uid = Column(Integer)  # 接受者uid
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间
