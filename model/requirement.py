#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import model


class RequirementModel(BaseModel):
    """需求信息"""
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)  # 自增
    passport_id = Column(Integer)  # passport_id
    sex = Column(String, default='未知')  # 性别：MODEL_SEX_ENUMERATE
    min_birth_year = Column(Integer, default=0)  # 最小出生年份
    max_birth_year = Column(Integer, default=0)  # 最大出生年份
    min_weight = Column(Integer, default=0)  # 最小体重(kg)
    max_weight = Column(Integer, default=0)  # 最大体重(kg)
    min_height = Column(Integer, default=0)  # 最小身高(cm)
    max_height = Column(Integer, default=0)  # 最大身高(cm)
    home_province = Column(String, default="")  # 籍贯省
    home_city = Column(String, default="")  # 籍贯市
    home_area = Column(String, default="")  # 籍贯区县
    province = Column(String, default="")  # 省
    city = Column(String, default="")  # 市
    school = Column(String, default="")  # 学校
    major = Column(String, default="")  # 专业
    study_from_year = Column(Integer, default=0)  # 入学年份 0不限
    school_type = Column(String, default="")  # 学校类型985211双一流本科专科
    martial_status = Column(String, default='不限')  # 婚姻现状：不限，未婚，离异
    max_month_pay = Column(Integer, default=0)  # 月收入(元-元)
    min_month_pay = Column(Integer, default=0)  # 月收入(元-元)
    min_education = Column(String, default='不限')  # 最低学历
    max_education = Column(String, default='不限')  # 最高学历
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getByPassportId(cls, dbSession, passportId):
        return dbSession.query(cls).filter(cls.passport_id == passportId, cls.status == model.MODEL_STATUS_YES).first()

    @classmethod
    def addByPassportId(cls, dbSession, passportId):
        user = cls(
            passport_id=passportId,
            status=model.MODEL_STATUS_YES
        )
        dbSession.add(user)
        dbSession.flush()
        return user

    @classmethod
    def updateByPassportId(cls, dbSession, passportId, **updateParams):
        dbSession.query(cls).filter(cls.passport_id == passportId, cls.status == model.MODEL_STATUS_YES).update(updateParams)
        dbSession.commit()
