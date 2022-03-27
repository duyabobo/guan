#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util import const


class UserModel(BaseModel):
    """用户信息"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)  # 自增
    passport_id = Column(Integer)  # passport_id
    sex = Column(String, default="未知")  # 性别：MODEL_SEX_ENUMERATE
    birth_year = Column(Integer, default=0)  # 出生年份
    martial_status = Column(String, default="未知")  # 婚姻现状：未知，未婚，离异
    height = Column(Integer, default=0)  # 身高(厘米-厘米)
    weight = Column(Integer, default=0)  # 体重(公斤-公斤)
    month_pay = Column(Integer, default=0)  # 月收入(元-元)
    education = Column(String, default="未知")  # 学历枚举
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getByPassportId(cls, dbSession, passportId):
        return dbSession.query(cls).filter(cls.passport_id == passportId, cls.status == const.MODEL_STATUS_YES).first()

    @classmethod
    def getByPassportIds(cls, dbSession, passportIds):
        return dbSession.query(cls).filter(cls.passport_id.in_(passportIds), cls.status == const.MODEL_STATUS_YES)

    @classmethod
    def addByPassportId(cls, dbSession, passportId):
        user = cls(
            passport_id=passportId,
            status=const.MODEL_STATUS_YES
        )
        dbSession.add(user)
        dbSession.flush()
        return user

    @classmethod
    def updateByPassportId(cls, dbSession, passportId, **updateParams):
        dbSession.query(cls).filter(cls.passport_id == passportId, cls.status == const.MODEL_STATUS_YES).update(updateParams)
        dbSession.commit()
