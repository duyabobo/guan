#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, func
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP

from model import BaseModel
from util.const.base import EMPTY_STR
from util.const.match import MODEL_STATUS_YES
from util.ctx import getDbSession


class EducationModel(BaseModel):
    """教育信息"""
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True)  # id
    region_id = Column(Integer, default=0)  # 学校所在区id，如果需要分校区的话，多个校区算多个记录
    school = Column(String, default=EMPTY_STR)  # 学校
    level = Column(String, default=EMPTY_STR)  # 学历枚举：EDUCATION_CHOICE_LIST
    major = Column(String, default=EMPTY_STR)  # 专业
    seq = Column(Integer, default=0)  # 序号越小越靠前。10位从高到低分配规则：1～5位支持42948个学校，6-7位支持99种学历类型，8-10位支持1000个专业
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getById(cls, educationId):
        return getDbSession().query(cls).filter(cls.id == educationId, cls.status == MODEL_STATUS_YES).first()

    @classmethod
    def addOne(cls, school, level, major):
        record = cls(
            school=school,
            level=level,
            major=major,
        )
        getDbSession().add(record)
        getDbSession().flush()
        return record

    @classmethod
    def getIdByEducation(cls, school, level, major):
        r = getDbSession().query(cls).filter(
            cls.school == school, cls.level == level,
            cls.major == major, cls.status == MODEL_STATUS_YES
        ).first()
        if not r:
            r = cls.addOne(school, level, major)
        return r.id

    @classmethod
    def getByRegionIds(cls, region_ids):
        if not region_ids:
            return []
        return getDbSession().query(cls).filter(cls.region_id.in_(region_ids)).order_by(cls.seq)

    @classmethod
    def getLevelsBySchool(cls, school):
        return getDbSession().query(cls.level).filter(cls.school == school).order_by(cls.seq)

    @classmethod
    def getMajorsBySchoolAndLevel(cls, school, level):
        return getDbSession().query(cls.major).filter(cls.school == school, cls.level == level).order_by(cls.seq)

    @classmethod
    def getSchoolsByRegionIds(cls, region_ids):
        if not region_ids:
            return []
        return getDbSession().query(cls.school).filter(cls.region_id.in_(region_ids)).order_by(cls.seq)
