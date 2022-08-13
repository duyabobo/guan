#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from ral.cache import checkInconsistentCache
from util.const.base import EMPTY_STR
from util.const.match import MODEL_STATUS_YES
from util.ctx import getDbSession


class RegionModel(BaseModel):
    """省市区数据"""
    __tablename__ = 'region'
    id = Column(Integer, primary_key=True)  # 自增
    province = Column(String, default=EMPTY_STR)  # 省份
    city = Column(String, default=EMPTY_STR)  # 市
    area = Column(String, default=EMPTY_STR)  # 区
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def addOne(cls, province, city, area):
        record = cls(
            province=province,
            city=city,
            area=area,
        )
        getDbSession().add(record)
        getDbSession().flush()
        return record

    @classmethod
    def getById(cls, reginId):
        return getDbSession().query(cls).filter(cls.id == reginId, cls.status == MODEL_STATUS_YES).first()

    @classmethod
    @checkInconsistentCache("RegionModel", ex=24 * 3600)
    def getIdByRegion(cls, province, city, area):
        r = getDbSession().query(cls).filter(
            cls.province == province, cls.city == city, cls.area == area, cls.status == MODEL_STATUS_YES
        ).first()
        if not r:
            r = cls.addOne(province, city, area)
        return r.id

    @classmethod
    @checkInconsistentCache("RegionModel", ex=24 * 3600)
    def listByProvince(cls, province):
        return getDbSession().query(cls).filter(cls.province == province, cls.status == MODEL_STATUS_YES).all()

    @classmethod
    @checkInconsistentCache("RegionModel", ex=24 * 3600)
    def listByProvinceAndCity(cls, province, city):
        return getDbSession().query(cls).filter(cls.province == province, cls.city == city, cls.status == MODEL_STATUS_YES).all()

    @classmethod
    @checkInconsistentCache("RegionModel", ex=24 * 3600)
    def listByProvinceAndCityAndArea(cls, province, city, area):
        return getDbSession().query(cls).filter(cls.province == province, cls.city == city, cls.area == area, cls.status == MODEL_STATUS_YES).all()
