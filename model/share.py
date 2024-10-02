#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from ral.cache import checkInconsistentCache
from util.const.match import MODEL_STATUS_YES
from util.ctx import getDbSession


class ShareModel(BaseModel):
    """分享信息"""
    __tablename__ = 'share'

    id = Column(Integer, primary_key=True)  # 自增
    share_passport_id = Column(Integer, default=0)  # 分享人passportId
    accept_passport_id = Column(Integer, default=0)  # 接受邀请人passportId
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def addOne(cls, share_passport_id, accept_passport_id):
        passport = cls(
            share_passport_id=share_passport_id,
            accept_passport_id=accept_passport_id
        )
        getDbSession().add(passport)
        getDbSession().flush()
        return passport

    @classmethod
    @checkInconsistentCache("ShareModel")
    def getAcceptCnt(cls, share_passport_id):
        return getDbSession().query(cls.share_passport_id == share_passport_id, cls.status == MODEL_STATUS_YES).count()
