#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.const.base import EMPTY_STR
from util.ctx import getDbSession


class VerifyModel(BaseModel):
    """认证信息"""
    __tablename__ = 'verify'
    id = Column(Integer, primary_key=True)  # 自增
    passport_id = Column(Integer)  # passport_id
    mail = Column(String, default=EMPTY_STR)  # 验证邮箱（需要加密）
    mail_type = Column(Integer, default=0)  # 邮箱类型：VERIFY_MAIL_TYPE
    mail_verify_status = Column(Integer, default=0)  # 工作认证状态: MODEL_MAIL_VERIFY_STATUS_ENUMERATE
    status = Column(Integer, default=1)  # 逻辑删除标示: MODEL_STATUS_ENUMERATE
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    create_time = Column(TIMESTAMP, default=func.now())  # 创建时间

    @classmethod
    def addByPassportId(cls, passportId):
        verify = cls(
            passport_id=passportId,
            status=match.MODEL_STATUS_YES
        )
        getDbSession().add(verify)
        getDbSession().flush()
        return verify

    @classmethod
    def getByPassportId(cls, passportId):
        return getDbSession().query(cls).filter(cls.passport_id == passportId, cls.status == match.MODEL_STATUS_YES).first()

    @classmethod
    def getMailType(cls, email):
        if match.MODEL_MAIL_KEYWORD in email:
            return match.MODEL_MAIL_TYPE_SCHOOL
        else:
            return match.MODEL_MAIL_TYPE_WORK

    @classmethod
    def updateVerifyStatus(cls, passportId, email):
        getDbSession().query(cls).filter(cls.passport_id == passportId).\
            update({"mail": email, "mail_type": cls.getMailType(email), "mail_verify_status": match.MODEL_MAIL_VERIFY_STATUS_YES})
        getDbSession().commit()

    @classmethod
    def fillWorkMail(cls, passportId, email):
        getDbSession().query(cls).filter(cls.passport_id == passportId).update({"mail": email})
        getDbSession().commit()
