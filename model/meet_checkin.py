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
from util.slot_blind import activity_slot_key

logger = logging.getLogger(__name__)


class MeetCheckinModel(BaseModel):
    """一次签到。对着这一笔已核销的定金，同一笔只记一次。"""
    __tablename__ = 'meet_checkin'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    slot_key = Column(String(64), default='')
    order_id = Column(Integer, default=0)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def _commit(cls):
        getDbSession().commit()

    @classmethod
    def has_order(cls, passport_id, order_id):
        if not passport_id or not order_id:
            return False
        row = getDbSession().query(cls.id).filter(
            cls.passport_id == passport_id,
            cls.order_id == order_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        return row is not None

    @classmethod
    def checked_order_ids(cls, order_ids):
        ids = [order_id for order_id in order_ids or [] if order_id]
        if not ids:
            return set()
        rows = getDbSession().query(cls.order_id).filter(
            cls.order_id.in_(ids),
            cls.status == match.MODEL_STATUS_YES,
        ).all()
        return {row.order_id for row in rows}

    @classmethod
    def add_once(cls, passport_id, activity_id, order_id):
        slot = activity_slot_key(activity_id)
        if not slot or not order_id:
            logger.error("签到未记下 passport=%s activity=%s", passport_id, activity_id)
            return None
        session = getDbSession()
        existing = session.query(cls).filter(
            cls.passport_id == passport_id,
            cls.order_id == order_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if existing:
            logger.info("已经签到 passport=%s order=%s", passport_id, order_id)
            return existing
        row = cls(
            passport_id=passport_id,
            slot_key=slot,
            order_id=order_id,
            status=match.MODEL_STATUS_YES,
        )
        session.add(row)
        session.flush()
        cls._commit()
        logger.info("已签到 passport=%s activity=%s order=%s", passport_id, activity_id, order_id)
        return row
