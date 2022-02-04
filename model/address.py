#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Address(Base):
    """地点"""
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)  # 自增
    name = Column(String)  # name
    description = Column(String)  # 地点描述(人均消费/吃喝玩乐推荐)
    location_id = Column(Integer)  # (省市区表)地区id
    longitude = Column(Float)  # 经度
    latitude = Column(Float)  # 纬度
    status = Column(Integer, default=1)  # 逻辑删除标示: 0已删除，1有效
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

