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

logger = logging.getLogger(__name__)


class PassportModel(BaseModel):
    """账号。身份只留编号、手机号密文、unionid 查找值。"""
    __tablename__ = 'passport'
    id = Column(Integer, primary_key=True)
    phone = Column(String(128), default='')  # 用 unionid 材料加密后的手机号
    unionid = Column(String(64))  # 身份密钥材料的 HMAC，不存明文
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def get_by_union_key(cls, union_key):
        if not union_key:
            return None
        return getDbSession().query(cls).filter(
            cls.unionid == union_key,
            cls.status == match.MODEL_STATUS_YES,
        ).first()

    @classmethod
    def add_with_union_key(cls, union_key):
        if not union_key:
            logger.error("拒绝创建没有身份查找值的通行证")
            return None
        passport = cls(
            unionid=union_key,
            phone='',
            status=match.MODEL_STATUS_YES,
        )
        getDbSession().add(passport)
        getDbSession().flush()
        logger.info("已创建通行证 passport=%s", passport.id)
        return passport

    @classmethod
    def save_phone(cls, passport_id, sealed):
        if not passport_id or not sealed:
            return False
        updated = getDbSession().query(cls).filter(
            cls.id == passport_id,
            cls.status == match.MODEL_STATUS_YES,
        ).update({cls.phone: sealed}, synchronize_session=False)
        getDbSession().flush()
        logger.info("手机号已加密写入 passport=%s updated=%s", passport_id, updated)
        return bool(updated)

    @classmethod
    def phone_cipher(cls, passport_id):
        if not passport_id:
            return ''
        row = getDbSession().query(cls.phone).filter(
            cls.id == passport_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if not row:
            return ''
        return row[0] or ''

    @classmethod
    def phone_ciphers(cls, passport_ids):
        ids = [passport_id for passport_id in passport_ids if passport_id]
        if not ids:
            return {}
        rows = getDbSession().query(cls.id, cls.phone).filter(
            cls.id.in_(ids),
            cls.status == match.MODEL_STATUS_YES,
            cls.phone != '',
        ).all()
        return {row.id: row.phone for row in rows if row.phone}

    @classmethod
    def list_ids_after(cls, after_id, limit):
        if limit <= 0:
            return []
        rows = getDbSession().query(cls.id).filter(
            cls.status == match.MODEL_STATUS_YES,
            cls.id > int(after_id or 0),
        ).order_by(cls.id.asc()).limit(limit).all()
        return [row.id for row in rows]

    @classmethod
    def getById(cls, passport_id):
        if not passport_id:
            return None
        return getDbSession().query(cls).filter(
            cls.id == passport_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
