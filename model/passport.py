#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Passport(Base):
    """账号"""
    __tablename__ = 'passport'
    id = Column(Integer, primary_key=True)  # 自增
    phone = Column(String)  # 手机号
    openid = Column(String)  # 微信openid
    status = Column(Integer, default=1)  # 逻辑删除标示: 0已删除，1有效
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def get_by_openid(cls, dbSession, openid):
        return dbSession.query(cls).filter(cls.openid == openid).first()

    @classmethod
    def add_by_openid(cls, dbSession, openid):
        passport = cls(
            openid=openid,
            phone="",
        )
        dbSession.add(passport)
        dbSession.flush()
        return passport
