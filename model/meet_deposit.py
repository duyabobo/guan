#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from model import BaseModel
from util.const import match
from util.const.deposit import OUTCOME_SKIP, PAYOUT_PENDING
from util.ctx import getDbSession

logger = logging.getLogger(__name__)


class MeetDepositSettleModel(BaseModel):
    """一对定金结算一次。用两笔订单号区分同一场之后的下一对。"""
    __tablename__ = 'meet_deposit_settle'
    id = Column(Integer, primary_key=True)
    slot_key = Column(String(64), default='')
    order_low_id = Column(Integer, default=0)
    order_high_id = Column(Integer, default=0)
    outcome = Column(String(16), default='')
    winner_passport_id = Column(Integer, default=0)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def _commit(cls):
        getDbSession().commit()

    @classmethod
    def done_pairs(cls, slots):
        keys = [slot for slot in slots or [] if slot]
        if not keys:
            return set()
        rows = getDbSession().query(cls).filter(
            cls.slot_key.in_(keys),
            cls.status == match.MODEL_STATUS_YES,
        ).all()
        return {(row.slot_key, row.order_low_id, row.order_high_id) for row in rows}

    @classmethod
    def add_once(cls, slot, order_low_id, order_high_id, outcome, winner_passport_id):
        if not slot:
            logger.error("定金结算未记下，盲索引为空")
            return False
        session = getDbSession()
        row = cls(
            slot_key=slot,
            order_low_id=order_low_id or 0,
            order_high_id=order_high_id or 0,
            outcome=outcome or OUTCOME_SKIP,
            winner_passport_id=winner_passport_id or 0,
            status=match.MODEL_STATUS_YES,
        )
        session.add(row)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            logger.info("定金已结算 low=%s high=%s", order_low_id, order_high_id)
            return False
        cls._commit()
        logger.info(
            "定金已结算 outcome=%s winner=%s low=%s high=%s",
            outcome, winner_passport_id, order_low_id, order_high_id,
        )
        return True


class MeetDepositPayoutModel(BaseModel):
    """记给按时到场的人的那一笔。微信退款只能退回原付款人，这里不打款。"""
    __tablename__ = 'meet_deposit_payout'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    slot_key = Column(String(64), default='')
    source_order_id = Column(Integer, default=0)
    amount_fen = Column(Integer, default=0)
    pay_status = Column(Integer, default=0)
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def _commit(cls):
        getDbSession().commit()

    @classmethod
    def add_once(cls, passport_id, slot, source_order_id, amount_fen):
        if not passport_id or not source_order_id:
            logger.info("定金未记给对方 passport=%s order=%s", passport_id, source_order_id)
            return None
        session = getDbSession()
        existing = session.query(cls).filter(
            cls.source_order_id == source_order_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()
        if existing:
            logger.info("定金已经记给对方 order=%s", source_order_id)
            return existing
        row = cls(
            passport_id=passport_id,
            slot_key=slot or '',
            source_order_id=source_order_id,
            amount_fen=amount_fen or 0,
            pay_status=PAYOUT_PENDING,
            status=match.MODEL_STATUS_YES,
        )
        session.add(row)
        session.flush()
        cls._commit()
        logger.info(
            "对方定金已记下，微信退款不能转给另一个人 passport=%s order=%s amount=%s",
            passport_id, source_order_id, amount_fen,
        )
        return row

    @classmethod
    def count_pending(cls):
        return getDbSession().query(cls.id).filter(
            cls.pay_status == PAYOUT_PENDING,
            cls.status == match.MODEL_STATUS_YES,
        ).count()
