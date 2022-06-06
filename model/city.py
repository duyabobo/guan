#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel


class CityModel(BaseModel):
    """市"""
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)  # 自增
    province_id = Column(Integer, default=0)  # 省id
    name = Column(String, default='')  # 市名
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间
