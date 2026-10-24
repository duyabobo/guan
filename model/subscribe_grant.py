#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func

from model import BaseModel
from util.const import match
from util.const.notice import SUBSCRIBE_REMAIN_CAP
from util.ctx import getDbSession

logger = logging.getLogger(__name__)


class SubscribeGrantModel(BaseModel):
    """一次授权加一次可发送额度。openid 只存密文。"""
    __tablename__ = 'subscribe_grant'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    template_id = Column(String(64), default='')
    openid_nonce = Column(String(32), default='')
    openid_cipher = Column(LargeBinary)
    remain = Column(Integer, default=0)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def grant(cls, passport_id, template_id, nonce, cipher_bytes):
        session = getDbSession()
        row = session.query(cls).filter(
            cls.passport_id == passport_id,
            cls.template_id == template_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if row:
            row.openid_nonce = nonce
            row.openid_cipher = cipher_bytes
            if row.remain < SUBSCRIBE_REMAIN_CAP:
                row.remain = (row.remain or 0) + 1
            else:
                logger.info("订阅额度已满 passport=%s remain=%s", passport_id, row.remain)
            session.flush()
            logger.info("订阅额度 passport=%s remain=%s", passport_id, row.remain)
            return row
        row = cls(
            passport_id=passport_id,
            template_id=template_id,
            openid_nonce=nonce,
            openid_cipher=cipher_bytes,
            remain=1,
            status=match.MODEL_STATUS_YES,
        )
        session.add(row)
        session.flush()
        logger.info("订阅额度 passport=%s remain=1", passport_id)
        return row

    @classmethod
    def map_by_passports(cls, passport_ids, template_id):
        ids = [passport_id for passport_id in passport_ids if passport_id]
        if not ids or not template_id:
            return {}
        rows = getDbSession().query(cls).filter(
            cls.passport_id.in_(ids),
            cls.template_id == template_id,
            cls.status == match.MODEL_STATUS_YES,
        ).all()
        return {row.passport_id: row for row in rows}

    @classmethod
    def consume_remain(cls, passport_id, template_id, count):
        if not passport_id or not template_id or count <= 0:
            return 0
        updated = getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            cls.template_id == template_id,
            cls.remain >= count,
            cls.status == match.MODEL_STATUS_YES,
        ).update({cls.remain: cls.remain - count}, synchronize_session=False)
        logger.info("扣订阅额度 passport=%s count=%s updated=%s", passport_id, count, updated)
        return updated
