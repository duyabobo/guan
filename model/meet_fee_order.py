#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import logging

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.sql import or_, and_

from model import BaseModel
from util.const import match
from util.const.meet_fee import (
    FEE_ORDER_CLOSED,
    FEE_ORDER_CONSUMED,
    FEE_ORDER_AWARDED,
    FEE_ORDER_CREATED,
    FEE_ORDER_FORFEIT,
    FEE_ORDER_PAID,
    FEE_ORDER_REFUND_PENDING,
    FEE_ORDER_REFUNDED,
    PREPAY_REUSE_MINUTES,
    format_out_trade_no,
)
from util.ctx import getDbSession
from util.slot_blind import activity_slot_key

logger = logging.getLogger(__name__)


class MeetFeeOrderModel(BaseModel):
    """一笔单次见面支付。写完就提交，避免外层回滚把待支付单抹掉。"""
    __tablename__ = 'meet_fee_order'
    id = Column(Integer, primary_key=True)
    passport_id = Column(Integer, default=0)
    activity_id = Column(Integer, default=0)  # 不再写入真实场次编号
    slot_key = Column(String(64), default='')
    out_trade_no = Column(String(32), default='')
    amount_fen = Column(Integer, default=0)
    pay_status = Column(Integer, default=0)
    prepay_id = Column(String(64), default='')
    wx_transaction_id = Column(String(64), default='')
    status = Column(Integer, default=1)
    update_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    create_time = Column(TIMESTAMP, default=func.now())

    @classmethod
    def _commit(cls):
        getDbSession().commit()

    @classmethod
    def find_paid(cls, passport_id, activity_id):
        return getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            _for_activity(cls, activity_id),
            cls.pay_status == FEE_ORDER_PAID,
            cls.status == match.MODEL_STATUS_YES,
        ).order_by(cls.id.desc()).first()

    @classmethod
    def find_reusable_created(cls, passport_id, activity_id, now):
        earliest = now - datetime.timedelta(minutes=PREPAY_REUSE_MINUTES)
        return getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            _for_activity(cls, activity_id),
            cls.pay_status == FEE_ORDER_CREATED,
            cls.prepay_id != '',
            cls.create_time >= earliest,
            cls.status == match.MODEL_STATUS_YES,
        ).order_by(cls.id.desc()).first()

    @classmethod
    def find_latest_created(cls, passport_id, activity_id):
        return getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            _for_activity(cls, activity_id),
            cls.pay_status == FEE_ORDER_CREATED,
            cls.status == match.MODEL_STATUS_YES,
        ).order_by(cls.id.desc()).first()

    @classmethod
    def get_by_out_trade_no(cls, out_trade_no):
        if not out_trade_no:
            return None
        return getDbSession().query(cls).filter(
            cls.out_trade_no == out_trade_no,
            cls.status == match.MODEL_STATUS_YES,
        ).first()

    @classmethod
    def get_by_id(cls, order_id):
        if not order_id:
            return None
        return getDbSession().query(cls).filter(
            cls.id == order_id,
            cls.status == match.MODEL_STATUS_YES,
        ).first()

    @classmethod
    def add_created(cls, passport_id, activity_id, amount_fen):
        session = getDbSession()
        slot = activity_slot_key(activity_id)
        if not slot:
            logger.error("见面支付单未建，盲索引为空 passport=%s activity=%s", passport_id, activity_id)
            return None
        row = cls(
            passport_id=passport_id,
            activity_id=0,
            slot_key=slot,
            out_trade_no='',
            amount_fen=amount_fen,
            pay_status=FEE_ORDER_CREATED,
            status=match.MODEL_STATUS_YES,
        )
        session.add(row)
        session.flush()
        row.out_trade_no = format_out_trade_no(row.id)
        cls._commit()
        logger.info("已建见面支付单 order=%s passport=%s activity=%s", row.id, passport_id, activity_id)
        return row

    @classmethod
    def save_prepay(cls, order_id, prepay_id):
        getDbSession().query(cls).filter(cls.id == order_id).update({
            cls.prepay_id: prepay_id,
        }, synchronize_session=False)
        cls._commit()
        logger.info("已写入预支付号 order=%s", order_id)

    @classmethod
    def close(cls, order_id):
        getDbSession().query(cls).filter(
            cls.id == order_id,
            cls.pay_status == FEE_ORDER_CREATED,
        ).update({cls.pay_status: FEE_ORDER_CLOSED}, synchronize_session=False)
        cls._commit()
        logger.info("已关闭见面支付单 order=%s", order_id)

    @classmethod
    def mark_paid(cls, order_id, transaction_id):
        updated = getDbSession().query(cls).filter(
            cls.id == order_id,
            cls.pay_status == FEE_ORDER_CREATED,
        ).update({
            cls.pay_status: FEE_ORDER_PAID,
            cls.wx_transaction_id: transaction_id or '',
        }, synchronize_session=False)
        cls._commit()
        logger.info("见面支付单已支付 order=%s updated=%s", order_id, updated)
        return updated

    @classmethod
    def consume(cls, order_id):
        updated = getDbSession().query(cls).filter(
            cls.id == order_id,
            cls.pay_status == FEE_ORDER_PAID,
        ).update({cls.pay_status: FEE_ORDER_CONSUMED}, synchronize_session=False)
        cls._commit()
        logger.info("见面支付单已核销 order=%s updated=%s", order_id, updated)
        return updated

    @classmethod
    def find_consumed(cls, passport_id, activity_id):
        return getDbSession().query(cls).filter(
            cls.passport_id == passport_id,
            _for_activity(cls, activity_id),
            cls.pay_status == FEE_ORDER_CONSUMED,
            cls.status == match.MODEL_STATUS_YES,
        ).order_by(cls.id.desc()).first()

    @classmethod
    def list_settle_orders(cls, slots):
        """结算要看核销、已退、已记给对方、不退。中途失败后下一轮还能对上同一对。"""
        keys = [slot for slot in slots or [] if slot]
        if not keys:
            return []
        statuses = (
            FEE_ORDER_CONSUMED,
            FEE_ORDER_AWARDED,
            FEE_ORDER_FORFEIT,
            FEE_ORDER_REFUND_PENDING,
            FEE_ORDER_REFUNDED,
        )
        return getDbSession().query(cls).filter(
            cls.slot_key.in_(keys),
            cls.pay_status.in_(statuses),
            cls.status == match.MODEL_STATUS_YES,
        ).all()

    @classmethod
    def mark_awarded(cls, order_id):
        updated = getDbSession().query(cls).filter(
            cls.id == order_id,
            cls.pay_status == FEE_ORDER_CONSUMED,
        ).update({cls.pay_status: FEE_ORDER_AWARDED}, synchronize_session=False)
        cls._commit()
        logger.info("定金改记给对方 order=%s updated=%s", order_id, updated)
        return updated

    @classmethod
    def mark_forfeit(cls, order_id):
        updated = getDbSession().query(cls).filter(
            cls.id == order_id,
            cls.pay_status == FEE_ORDER_CONSUMED,
        ).update({cls.pay_status: FEE_ORDER_FORFEIT}, synchronize_session=False)
        cls._commit()
        logger.info("定金不退 order=%s updated=%s", order_id, updated)
        return updated

    @classmethod
    def mark_refund_pending(cls, order_id):
        updated = getDbSession().query(cls).filter(
            cls.id == order_id,
            cls.pay_status.in_((FEE_ORDER_PAID, FEE_ORDER_CONSUMED)),
        ).update({cls.pay_status: FEE_ORDER_REFUND_PENDING}, synchronize_session=False)
        cls._commit()
        logger.info("见面支付单待退款 order=%s updated=%s", order_id, updated)
        return updated

    @classmethod
    def mark_refunded(cls, order_id):
        getDbSession().query(cls).filter(cls.id == order_id).update({
            cls.pay_status: FEE_ORDER_REFUNDED,
        }, synchronize_session=False)
        cls._commit()
        logger.info("见面支付单已退款 order=%s", order_id)

    @classmethod
    def list_refund_pending(cls, limit):
        return getDbSession().query(cls).filter(
            cls.pay_status == FEE_ORDER_REFUND_PENDING,
            cls.status == match.MODEL_STATUS_YES,
        ).order_by(cls.id.asc()).limit(limit).all()


def _for_activity(model, activity_id):
    slot = activity_slot_key(activity_id)
    if not slot:
        return model.activity_id == activity_id
    return or_(
        model.slot_key == slot,
        and_(model.activity_id == activity_id, model.slot_key == ''),
    )
