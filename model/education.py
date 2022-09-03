#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP

from model import BaseModel
from ral.cache import checkInconsistentCache
from util.const.base import EMPTY_STR
from util.const.match import MODEL_STATUS_YES
from util.ctx import getDbSession


class EducationModel(BaseModel):
    """教育信息"""
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)  # id
    category = Column(String, default=EMPTY_STR)  # 专业门类
    disciplines = Column(String, default=EMPTY_STR)  # 专业类(学科）
    major = Column(String, default=EMPTY_STR)  # 专业
    seq = Column(Integer, default=0)  # 序号越小越靠前
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getById(cls, educationId):
        return getDbSession().query(cls).filter(cls.id == educationId, cls.status == MODEL_STATUS_YES).first()

    @classmethod
    def addOne(cls, category, disciplines, major):
        record = cls(
            category=category,
            disciplines=disciplines,
            major=major,
        )
        getDbSession().add(record)
        getDbSession().flush()
        return record

    @classmethod
    @checkInconsistentCache("EducationModel", ex=24*3600)
    def getIdByData(cls, category, disciplines, major):
        r = getDbSession().query(cls).filter(
            cls.category == category, cls.disciplines == disciplines,
            cls.major == major, cls.status == MODEL_STATUS_YES
        ).first()
        if not r:
            r = cls.addOne(category, disciplines, major)
        return r.id

    @classmethod
    @checkInconsistentCache("EducationModel", ex=24 * 3600)
    def getFirstsByRegionids(cls):
        return getDbSession().query(cls.category).order_by(cls.seq).all()

    @classmethod
    @checkInconsistentCache("EducationModel", ex=24 * 3600)
    def getSecondsByFirst(cls, category):
        return getDbSession().query(cls.disciplines).filter(cls.category == category).order_by(cls.seq).all()

    @classmethod
    @checkInconsistentCache("EducationModel", ex=24 * 3600)
    def getThirdsByFirstAndSecond(cls, category, disciplines):
        return getDbSession().query(cls.major).filter(cls.category == category, cls.disciplines == disciplines).order_by(cls.seq).all()
