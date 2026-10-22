#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.dialects.mysql import MEDIUMBLOB

from model import BaseModel
from util.const import match
from util.ctx import getDbSession

logger = logging.getLogger(__name__)


class SensitiveRecordModel(BaseModel):
    """敏感信息密文。表内没有密钥。"""

    __tablename__ = 'sensitive_record'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    kind = Column(String(16), default='')
    key_provider = Column(String(32), default='')
    nonce = Column(String(32), default='')
    cipher_text = Column(MEDIUMBLOB)
    content_type = Column(String(64), default='')
    plain_length = Column(Integer, default=0)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def add(cls, passport_id, kind, key_provider, nonce, cipher_text, content_type, plain_length):
        row = cls(
            passport_id=passport_id,
            kind=kind,
            key_provider=key_provider,
            nonce=nonce,
            cipher_text=cipher_text,
            content_type=content_type,
            plain_length=plain_length,
            status=match.MODEL_STATUS_YES,
        )
        session = getDbSession()
        session.add(row)
        session.flush()
        logger.info(
            "敏感信息已加密写入 passport=%s kind=%s record=%s bytes=%s provider=%s",
            passport_id, kind, row.id, plain_length, key_provider,
        )
        return row

    @classmethod
    def latest(cls, passport_id, kind):
        if not passport_id or not kind:
            return None
        return getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            cls.kind == kind,
            cls.status == match.MODEL_STATUS_YES,
        ).order_by(cls.id.desc()).first()
