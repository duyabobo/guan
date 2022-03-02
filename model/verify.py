#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util import const


class VerifyModel(BaseModel):
    """认证信息"""
    __tablename__ = 'verify'
    id = Column(Integer, primary_key=True)  # 自增
    passport_id = Column(Integer)  # passport_id
    work_mail = Column(String, default="")  # 工作邮箱（需要加密）
    work_verify_status = Column(Integer, default=0)  # 工作认证状态: MODEL_WORK_VERIFY_STATUS_ENUMERATE
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def addByPassportId(cls, dbSession, passportId):
        verify = cls(
            passport_id=passportId,
            status=const.MODEL_STATUS_YES
        )
        dbSession.add(verify)
        dbSession.flush()
        return verify

    @classmethod
    def getByPassportId(cls, dbSession, passportId):
        return dbSession.query(cls).filter(cls.passport_id == passportId, cls.status == const.MODEL_STATUS_YES).first()

    @classmethod
    def updateVerifyStatus(cls, dbSession, passportId, email):
        dbSession.query(cls).filter(cls.passport_id == passportId).\
            update({"work_mail": email, "work_verify_status": const.MODEL_WORK_VERIFY_STATUS_YES})
        dbSession.commit()

    @classmethod
    def fillWorkMail(cls, dbSession, passportId, email):
        dbSession.query(cls).filter(cls.passport_id == passportId).update({"work_mail": email})
        dbSession.commit()
