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


class WorkModel(BaseModel):
    """工作信息"""
    __tablename__ = 'work'
    id = Column(Integer, primary_key=True)  # id
    profession = Column(String, default=EMPTY_STR)  # 行业
    industry = Column(String, default=EMPTY_STR)  # 方向
    position = Column(String, default=EMPTY_STR)  # 职位
    seq = Column(Integer, default=0)  # 序号越小越靠前
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getById(cls, workId):
        return getDbSession().query(cls).filter(cls.id == workId, cls.status == MODEL_STATUS_YES).first()

    @classmethod
    def addOne(cls, region_id, profession, industry, position):
        record = cls(
            region_id=region_id,
            profession=profession,
            industry=industry,
            position=position,
        )
        getDbSession().add(record)
        getDbSession().flush()
        return record

    @classmethod
    @checkInconsistentCache("WorkModel", ex=24*3600)
    def getIdByData(cls, region_id, profession, industry, position):
        r = getDbSession().query(cls).filter(
            cls.region_id == region_id,
            cls.profession == profession, cls.industry == industry,
            cls.position == position, cls.status == MODEL_STATUS_YES
        ).first()
        if not r:
            r = cls.addOne(region_id, profession, industry, position)
        return r.id

    @classmethod
    @checkInconsistentCache("WorkModel", ex=24 * 3600)
    def getSecondsByFirst(cls, profession):
        return getDbSession().query(cls.industry).filter(cls.profession == profession).order_by(cls.seq).all()

    @classmethod
    @checkInconsistentCache("WorkModel", ex=24 * 3600)
    def getThirdsByFirstAndSecond(cls, profession, industry):
        return getDbSession().query(cls.position).filter(cls.profession == profession, cls.industry == industry).order_by(cls.seq).all()

    @classmethod
    @checkInconsistentCache("WorkModel", ex=24 * 3600)
    def getFirstsByRegionids(cls, region_ids):
        if not region_ids:
            return []
        return getDbSession().query(cls.profession).filter(cls.region_id.in_(region_ids)).order_by(cls.seq).all()
