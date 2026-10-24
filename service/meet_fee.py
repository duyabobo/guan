#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""单次见面要不要付钱，以及微信支付单的创建、确认和退款。"""
import datetime
import logging
import secrets
import time
import xml.etree.ElementTree as ET

from model.meet_fee_order import MeetFeeOrderModel
from model.passport import PassportModel
from util.config import get_conf
from util.const.meet_fee import (
    FEE_ORDER_CREATED,
    FEE_ORDER_REFUND_PENDING,
    FEE_REFUNDABLE_STATUSES,
    FEN_PER_YUAN,
    LOCAL_PAY_IP,
    PAY_BODY,
    PAY_NOTIFY_FAIL_XML,
    PAY_NOTIFY_SUCCESS_XML,
    REFUND_BATCH_LIMIT,
    WX_PAY_TIMEOUT_SEC,
    WX_SUCCESS,
    WX_TRADE_JSAPI,
    format_out_refund_no,
)
from util.const.response import (
    RESP_MEET_FEE_OPENID,
    RESP_MEET_FEE_UNAVAILABLE,
)
from util.encode import md5_hex
from util.wx_pay import (
    client_pay_params,
    parse_xml,
    query_order,
    refund_order,
    sign_matches,
    unified_order,
)

logger = logging.getLogger(__name__)

_READY_KEYS = ('appid', 'mch_id', 'mch_key', 'notify_url')


class FeeOutcome(object):
    def __init__(self, order_id=0, pay=None, msg=None):
        self.order_id = order_id
        self.pay = pay
        self.msg = msg


def pay_settings():
    return {
        'appid': get_conf('appid', '', 'weixin'),
        'mch_id': get_conf('mch_id', '', 'weixin'),
        'mch_key': get_conf('mch_key', '', 'weixin'),
        'notify_url': get_conf('pay_notify_url', '', 'weixin'),
        'cert_file': get_conf('mch_cert_file', '', 'weixin'),
        'key_file': get_conf('mch_key_file', '', 'weixin'),
    }


def pay_ready(settings):
    return all(settings.get(key) for key in _READY_KEYS)


def openid_belongs_to(passport_id, openid):
    if not passport_id or not openid:
        return False
    passport = PassportModel.getById(passport_id)
    if not passport or not passport.openid:
        return False
    return passport.openid == md5_hex(openid)


class MeetFeeService(object):

    @staticmethod
    def ensure(passport_id, activity_id, openid, client_ip, amount_fen):
        """已支付且金额仍是当前费用则返回订单。否则按这次的金额拉起支付，不改座位。"""
        paid = MeetFeeOrderModel.find_paid(passport_id, activity_id)
        if paid and paid.amount_fen == amount_fen:
            logger.info("见面支付沿用已支付单 order=%s passport=%s", paid.id, passport_id)
            return FeeOutcome(order_id=paid.id)
        if paid:
            logger.info("已支付金额和当前费用不一致 order=%s", paid.id)
            MeetFeeService.refund(paid.id)
        created = MeetFeeOrderModel.find_latest_created(passport_id, activity_id)
        if created and _remote_paid(created):
            if created.amount_fen == amount_fen:
                return FeeOutcome(order_id=created.id)
            logger.info("查单金额和当前费用不一致 order=%s", created.id)
            MeetFeeService.refund(created.id)
            return _create_prepay(passport_id, activity_id, openid, client_ip, amount_fen)
        reusable = MeetFeeOrderModel.find_reusable_created(passport_id, activity_id, _now())
        if reusable and reusable.prepay_id and reusable.amount_fen == amount_fen:
            if not pay_ready(pay_settings()):
                logger.info("见面付费未开通，不能复用预支付单 passport=%s", passport_id)
                return FeeOutcome(msg=RESP_MEET_FEE_UNAVAILABLE)
            logger.info("见面支付复用预支付单 order=%s passport=%s", reusable.id, passport_id)
            return FeeOutcome(pay=_pay_payload(reusable.prepay_id, amount_fen))
        if reusable and reusable.amount_fen != amount_fen:
            logger.info("预支付金额和当前费用不一致 order=%s", reusable.id)
            MeetFeeOrderModel.close(reusable.id)
        return _create_prepay(passport_id, activity_id, openid, client_ip, amount_fen)

    @staticmethod
    def refund(order_id):
        order = MeetFeeOrderModel.get_by_id(order_id)
        if not order or order.pay_status not in FEE_REFUNDABLE_STATUSES:
            logger.info("退款跳过 order=%s", order_id)
            return
        if order.pay_status != FEE_ORDER_REFUND_PENDING:
            MeetFeeOrderModel.mark_refund_pending(order_id)
        _send_refund(order_id)

    @staticmethod
    def retry_refunds():
        orders = MeetFeeOrderModel.list_refund_pending(REFUND_BATCH_LIMIT)
        if not orders:
            return
        settings = pay_settings()
        if not settings['cert_file'] or not settings['key_file']:
            logger.info("退款未发出，缺少商户证书 count=%s", len(orders))
            return
        logger.info("待退款 %s 笔", len(orders))
        for order in orders:
            _send_refund(order.id)

    @staticmethod
    def handle_notify(raw):
        settings = pay_settings()
        if not settings['mch_key']:
            logger.info("支付回调缺少商户密钥")
            return PAY_NOTIFY_FAIL_XML
        parsed = _parse_notify(raw)
        if parsed is None or not sign_matches(parsed, settings['mch_key']):
            logger.info("支付回调签名不符或无法解析")
            return PAY_NOTIFY_FAIL_XML
        if parsed.get('return_code') != WX_SUCCESS or parsed.get('result_code') != WX_SUCCESS:
            logger.info("支付回调结果未成功")
            return PAY_NOTIFY_SUCCESS_XML
        order = MeetFeeOrderModel.get_by_out_trade_no(parsed.get('out_trade_no'))
        if not order:
            logger.info("支付回调没有对应订单")
            return PAY_NOTIFY_FAIL_XML
        if order.pay_status != FEE_ORDER_CREATED:
            logger.info("支付回调重复 order=%s pay_status=%s", order.id, order.pay_status)
            return PAY_NOTIFY_SUCCESS_XML
        if _fen(parsed.get('total_fee')) != order.amount_fen:
            logger.info("支付回调金额不符 order=%s", order.id)
            return PAY_NOTIFY_FAIL_XML
        MeetFeeOrderModel.mark_paid(order.id, parsed.get('transaction_id') or '')
        return PAY_NOTIFY_SUCCESS_XML


def _now():
    return datetime.datetime.now()


def _fen(value):
    text = str(value or '')
    if not text.isdigit():
        return 0
    return int(text)


def _parse_notify(raw):
    try:
        return parse_xml(raw)
    except ET.ParseError:
        logger.info("支付回调不是合法 xml")
        return None


def _remote_paid(order):
    settings = pay_settings()
    if not pay_ready(settings) or not order.out_trade_no:
        return False
    try:
        parsed = query_order({
            'appid': settings['appid'],
            'mch_id': settings['mch_id'],
            'out_trade_no': order.out_trade_no,
            'nonce_str': secrets.token_hex(16),
        }, settings['mch_key'], WX_PAY_TIMEOUT_SEC)
    except Exception:
        logger.exception("微信查单失败 order=%s", order.id)
        return False
    if parsed.get('trade_state') != WX_SUCCESS:
        return False
    if _fen(parsed.get('total_fee')) != order.amount_fen:
        logger.info("查单金额不符 order=%s", order.id)
        return False
    MeetFeeOrderModel.mark_paid(order.id, parsed.get('transaction_id') or '')
    return True


def _create_prepay(passport_id, activity_id, openid, client_ip, amount_fen):
    settings = pay_settings()
    if not pay_ready(settings):
        logger.info("见面付费未开通 passport=%s", passport_id)
        return FeeOutcome(msg=RESP_MEET_FEE_UNAVAILABLE)
    if not openid_belongs_to(passport_id, openid):
        logger.info("见面支付 openid 与账号不一致 passport=%s", passport_id)
        return FeeOutcome(msg=RESP_MEET_FEE_OPENID)
    order = MeetFeeOrderModel.add_created(passport_id, activity_id, amount_fen)
    if not order:
        return FeeOutcome(msg=RESP_MEET_FEE_UNAVAILABLE)
    prepay_id = _unified(order, settings, openid, client_ip)
    if not prepay_id:
        MeetFeeOrderModel.close(order.id)
        return FeeOutcome(msg=RESP_MEET_FEE_UNAVAILABLE)
    MeetFeeOrderModel.save_prepay(order.id, prepay_id)
    return FeeOutcome(pay=_pay_payload(prepay_id, amount_fen))


def _unified(order, settings, openid, client_ip):
    try:
        return unified_order({
            'appid': settings['appid'],
            'mch_id': settings['mch_id'],
            'nonce_str': secrets.token_hex(16),
            'body': PAY_BODY,
            'out_trade_no': order.out_trade_no,
            'total_fee': order.amount_fen,
            'spbill_create_ip': client_ip or LOCAL_PAY_IP,
            'notify_url': settings['notify_url'],
            'trade_type': WX_TRADE_JSAPI,
            'openid': openid,
        }, settings['mch_key'], WX_PAY_TIMEOUT_SEC)
    except Exception:
        logger.exception("微信下单失败 order=%s", order.id)
        return ''


def _pay_payload(prepay_id, amount_fen):
    settings = pay_settings()
    yuan = amount_fen // FEN_PER_YUAN
    wx_params = client_pay_params(
        prepay_id,
        settings['appid'],
        settings['mch_key'],
        int(time.time()),
        secrets.token_hex(16),
    )
    return {
        'yuan': yuan,
        'buttonLabel': '支付%d元并继续' % yuan,
        'wx': wx_params,
    }


def _send_refund(order_id):
    order = MeetFeeOrderModel.get_by_id(order_id)
    settings = pay_settings()
    if not order or not settings['cert_file'] or not settings['key_file'] or not pay_ready(settings):
        logger.info("退款未发出 order=%s 缺少商户证书或支付配置", order_id)
        return
    try:
        ok = refund_order({
            'appid': settings['appid'],
            'mch_id': settings['mch_id'],
            'nonce_str': secrets.token_hex(16),
            'out_trade_no': order.out_trade_no,
            'out_refund_no': format_out_refund_no(order.id),
            'total_fee': order.amount_fen,
            'refund_fee': order.amount_fen,
        }, settings['mch_key'], WX_PAY_TIMEOUT_SEC, settings['cert_file'], settings['key_file'])
    except Exception:
        logger.exception("退款请求失败 order=%s", order_id)
        return
    if ok:
        MeetFeeOrderModel.mark_refunded(order_id)
