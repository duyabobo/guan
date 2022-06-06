#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel


class AreaModel(BaseModel):
    """县区"""
    __tablename__ = 'area'
    id = Column(Integer, primary_key=True)  # 自增
    province_id = Column(Integer, default=0)  # 省id
    city_id = Column(Integer, default=0)  # 市id
    name = Column(String, default='')  # 区县名
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间
