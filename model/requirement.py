#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from model.education import EducationModel
from model.region import RegionModel
from util.const import match
from util.const.base import ALL_STR, UNKNOWN_STR, NO_LIMIT_STR
from util.ctx import getDbSession


class RequirementModel(BaseModel):
    """需求信息"""
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)  # 自增
    passport_id = Column(Integer)  # passport_id
    verify_type = Column(Integer, default=0)  # 认证类型：MODEL_VERIFY_TYPE
    sex = Column(String, default=UNKNOWN_STR)  # 性别：MODEL_SEX_ENUMERATE
    min_birth_year = Column(Integer, default=0)  # 最小出生年份
    max_birth_year = Column(Integer, default=0)  # 最大出生年份
    min_weight = Column(Integer, default=0)  # 最小体重(kg)
    max_weight = Column(Integer, default=0)  # 最大体重(kg)
    min_height = Column(Integer, default=0)  # 最小身高(cm)
    max_height = Column(Integer, default=0)  # 最大身高(cm)
    home_region_id = Column(Integer, default=0)  # 籍贯地点id
    study_region_id = Column(Integer, default=0)  # 学习地点id
    education_id = Column(Integer, default=0)  # 学习信息id
    min_study_from_year = Column(Integer, default=0)  # 最早入学年份
    max_study_from_year = Column(Integer, default=0)  # 最晚入学年份
    martial_status = Column(String, default=NO_LIMIT_STR)  # 婚姻现状：不限，未婚，离异
    max_month_pay = Column(Integer, default=0)  # 月收入(元-元)
    min_month_pay = Column(Integer, default=0)  # 月收入(元-元)
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getByPassportId(cls, passportId):
        return getDbSession().query(cls).filter(cls.passport_id == passportId, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def addByPassportId(cls, passportId):
        user = cls(
            passport_id=passportId,
            status=match.MODEL_STATUS_YES
        )
        getDbSession().add(user)
        getDbSession().flush()
        return user

    @classmethod
    def updateByPassportId(cls, passportId, **updateParams):
        getDbSession().query(cls).filter(cls.passport_id == passportId, cls.status == match.MODEL_STATUS_YES).update(updateParams)
        getDbSession().commit()

    @property
    def home_region(self):
        """home_address_id"""
        return RegionModel.getById(self.home_region_id)

    @property
    def study_region(self):
        return RegionModel.getById(self.study_region_id)

    @property
    def education(self):
        return EducationModel.getById(self.education_id)

    @property
    def school(self):
        return self.education.school if self.education else ALL_STR

    @property
    def level(self):
        return self.education.level if self.education else ALL_STR

    @property
    def major(self):
        return self.education.major if self.education else ALL_STR
