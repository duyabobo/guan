#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.ctx import getDbSession
from util.encode import md5_hex

logger = logging.getLogger(__name__)


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
        openidMd5 = md5_hex(openid)
        return getDbSession().query(cls).filter(cls.openid == openidMd5, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def addByOpenid(cls, openid):
        openidMd5 = md5_hex(openid)
        passport = cls(
            openid=openidMd5,
            phone="",
            status=match.MODEL_STATUS_YES
        )
        getDbSession().add(passport)
        getDbSession().flush()
        return passport

    @classmethod
    def getById(cls, passport_id):
        if not passport_id:
            return None
        return getDbSession().query(cls).filter(
            cls.id == passport_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()

    @classmethod
    def addBare(cls):
        """还没有微信 openid 的通行证，留给后续其他身份提供方。"""
        passport = cls(
            openid='',
            phone='',
            status=match.MODEL_STATUS_YES,
        )
        getDbSession().add(passport)
        getDbSession().flush()
        logger.info("已创建未绑定微信的通行证 passport=%s", passport.id)
        return passport
