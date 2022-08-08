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
    school = Column(String, default=EMPTY_STR)  # 学校
    level = Column(String, default=EMPTY_STR)  # 学历枚举：EDUCATION_CHOICE_LIST
    major = Column(String, default=EMPTY_STR)  # 专业
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