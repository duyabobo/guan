#! /usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.ctx import getDbSession


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
    def getByOpenid(cls, openid):
        openidMd5 = hashlib.md5(openid).hexdigest()
        return getDbSession().query(cls).filter(cls.openid == openidMd5, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def addByOpenid(cls, openid):
        openidMd5 = hashlib.md5(openid).hexdigest()
        passport = cls(
            openid=openidMd5,
            phone="",
            status=match.MODEL_STATUS_YES
        )
        getDbSession().add(passport)
        getDbSession().flush()
        return passport
