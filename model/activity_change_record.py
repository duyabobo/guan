#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ActivityChangeRecord(Base):
    """活动变化流水记录"""
    __tablename__ = 'activity_change_record'
    id = Column(Integer, primary_key=True)  # 自增
    activity_id = Column(Integer)  # 活动id
    uid = Column(Integer)  # uid
    change_type = Column(Integer)  # 变化类型：0未知，1发出邀请，2接受邀请，3邀请者取消，4接受者取消
    status = Column(Integer, default=1)  # 逻辑删除标示: 0已删除，1有效
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间
