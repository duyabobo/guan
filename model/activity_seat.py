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
from util.ctx import getDbSession

logger = logging.getLogger(__name__)


class ActivitySeatModel(BaseModel):
    """谁坐在哪一场。场次编号在密文里，槽位只存盲索引。"""

    __tablename__ = 'activity_seat'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    slot_key = Column(String(64), default='')
    nonce = Column(String(32), default='')
    cipher_text = Column(LargeBinary)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def list_by_slots(cls, slot_keys):
        keys = [key for key in slot_keys if key]
        if not keys:
            return []
        return getDbSession().query(cls).filter(
            cls.slot_key.in_(keys),
            cls.status == match.MODEL_STATUS_YES,
        ).all()

    @classmethod
    def list_by_passport(cls, passport_id):
        if not passport_id:
            return []
        return cls.list_by_passports([passport_id])

    @classmethod
    def list_by_passports(cls, passport_ids):
        ids = [passport_id for passport_id in passport_ids if passport_id]
        if not ids:
            return []
        return getDbSession().query(cls).filter(
            cls.passport_id.in_(ids),
            cls.status == match.MODEL_STATUS_YES,
        ).all()

    @classmethod
    def save_seat(cls, passport_id, slot_key, nonce, cipher_text):
        session = getDbSession()
        row = session.query(cls).filter(
            cls.passport_id == passport_id,
            cls.slot_key == slot_key,
        ).first()
        if row is None:
            session.add(cls(
                passport_id=passport_id,
                slot_key=slot_key,
                nonce=nonce,
                cipher_text=cipher_text,
                status=match.MODEL_STATUS_YES,
            ))
            logger.info("已写入见面座位 passport=%s", passport_id)
            return
        row.nonce = nonce
        row.cipher_text = cipher_text
        row.status = match.MODEL_STATUS_YES
        logger.info("已更新见面座位 passport=%s", passport_id)

    @classmethod
    def clear_passport(cls, passport_id, slot_key):
        if not passport_id or not slot_key:
            return
        getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            cls.slot_key == slot_key,
            cls.status == match.MODEL_STATUS_YES,
        ).update({cls.status: match.MODEL_STATUS_NO}, synchronize_session=False)
        logger.info("已清掉见面座位 passport=%s", passport_id)
