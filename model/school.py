#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel


class SchoolModel(BaseModel):
    """学校信息"""
    __tablename__ = 'school'

    id = Column(Integer, primary_key=True)  # 自增
    region_id = Column(Integer, default=0)  # 地址id
    name = Column(String, default=0)  # 学校名(每个校区有一个记录)
    seq = Column(Integer, default=0)  # 序号越小越靠前
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间
