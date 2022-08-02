#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, SmallInteger
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from model.region import RegionModel
from util.const import match
from util.ctx import getDbSession


class UserModel(BaseModel):
    """用户信息"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)  # 自增
    has_fill_finish = Column(SmallInteger, default=0)  # 是否完善信息结束
    passport_id = Column(Integer, default=0)  # passport_id
    sex = Column(String, default="未知")  # 性别：MODEL_SEX_ENUMERATE
    birth_year = Column(Integer, default=0)  # 出生年份
    height = Column(Integer, default=0)  # 身高(厘米)
    weight = Column(Integer, default=0)  # 体重(公斤)
    home_region_id = Column(Integer, default=0)  # 籍贯地点id
    study_region_id = Column(Integer, default=0)  # 学习地点id
    study_from_year = Column(Integer, default=0)  # 入学年份
    education_id = Column(Integer, default=0)  # 学习信息id
    martial_status = Column(String, default="未知")  # 婚姻现状：未知，未婚，离异
    month_pay = Column(Integer, default=0)  # 月收入(元)
    is_fall_in_love = Column(Integer, default=0)  # 是否坠入爱河
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getByPassportId(cls, passportId):
        return getDbSession().query(cls).filter(cls.passport_id == passportId, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def getByPassportIds(cls, passportIds):
        return getDbSession().query(cls).filter(cls.passport_id.in_(passportIds), cls.status == match.MODEL_STATUS_YES)

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
    def sexIndex(self):
        return match.SEX_CHOICE_LIST.index(self.sex)

    @property
    def home_region(self):
        """home_address_id"""
        return RegionModel.getById(self.home_region_id)

    @property
    def study_region(self):
        return RegionModel.getById(self.study_region_id)
