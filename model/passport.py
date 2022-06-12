#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match


class PassportModel(BaseModel):
    """账号"""
    __tablename__ = 'passport'
    id = Column(Integer, primary_key=True)  # 自增
    phone = Column(String)  # 手机号
    openid = Column(String)  # 微信openid
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def getByOpenid(cls, dbSession, openid):
        return dbSession.query(cls).filter(cls.openid == openid, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def addByOpenid(cls, dbSession, openid):
        passport = cls(
            openid=openid,
            phone="",
            status=match.MODEL_STATUS_YES
        )
        dbSession.add(passport)
        dbSession.flush()
        return passport
