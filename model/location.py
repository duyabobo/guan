#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel


class LocationModel(BaseModel):
    """省市区"""
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)  # 自增
    province = Column(String)  # 省份
    city = Column(String)  # 市
    area = Column(String)  # 区
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间
