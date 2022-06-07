#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util import const


class AddressModel(BaseModel):
    """地点"""
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)  # 自增
    name = Column(String)  # name
    description = Column(String, default="")  # 地点描述(人均消费/吃喝玩乐推荐)
    img = Column(String, default="")
    province = Column(String, default="")  # 省名
    city = Column(String, default="")  # 市名
    area = Column(String, default="")  # 地区名
    longitude = Column(Float, default=0)  # 经度
    latitude = Column(Float, default=0)  # 纬度
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def listByLongitudeLatitude(cls, dbSession, longitude, latitude):  # todo
        return dbSession.query(cls).filter(cls.status == const.MODEL_STATUS_YES).all()

    @classmethod
    def getById(cls, dbSession, addressId):
        return dbSession.query(cls).filter(cls.id == addressId, cls.status == const.MODEL_STATUS_YES).first()

    @classmethod
    def getLastAddress(cls, dbSession):
        return dbSession.query(cls).filter(cls.status == const.MODEL_STATUS_YES).order_by(cls.id.desc()).first()

    @property
    def nameShort(self):
        if len(self.name) <= 8:
            return self.name
        else:
            return self.name[:8] + "..."

    @property
    def nameLong(self):
        if len(self.name) <= 22:
            return self.name
        else:
            return self.name[:22] + "..."
