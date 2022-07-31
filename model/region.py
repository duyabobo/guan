#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const.match import MODEL_STATUS_YES
from util.ctx import getDbSession


class RegionModel(BaseModel):
    """省市区数据"""
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)  # 自增
    province = Column(String, default='')  # 省份
    city = Column(String, default='')  # 市
    area = Column(String, default='')  # 区
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getById(cls, reginId):
        return getDbSession().query(cls).filter(cls.id == reginId, cls.status == MODEL_STATUS_YES).first()
