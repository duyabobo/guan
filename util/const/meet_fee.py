#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""见面定金的支付单状态。金额和结算规则在 util/const/deposit.py。"""

FEN_PER_YUAN = 100

FEE_ORDER_CREATED = 0
FEE_ORDER_PAID = 1
FEE_ORDER_CONSUMED = 2
FEE_ORDER_REFUND_PENDING = 3
FEE_ORDER_REFUNDED = 4
FEE_ORDER_CLOSED = 5
FEE_ORDER_AWARDED = 6
FEE_ORDER_FORFEIT = 7

FEE_REFUNDABLE_STATUSES = (
    FEE_ORDER_PAID,
    FEE_ORDER_CONSUMED,
    FEE_ORDER_REFUND_PENDING,
)

PREPAY_REUSE_MINUTES = 90
OUT_TRADE_NO_PREFIX = 'MF'
OUT_REFUND_NO_PREFIX = 'MR'
OUT_TRADE_NO_WIDTH = 20
PAY_BODY = '关关雎鸠见面定金'
PAY_NOTIFY_PATH = '/wx_pay_notify'
LOCAL_PAY_IP = '127.0.0.1'
REFUND_BATCH_LIMIT = 20
WX_PAY_TIMEOUT_SEC = 5
WX_SIGN_TYPE_MD5 = 'MD5'
WX_TRADE_JSAPI = 'JSAPI'
WX_SUCCESS = 'SUCCESS'

PAY_NOTIFY_SUCCESS_XML = (
    '<xml><return_code><![CDATA[SUCCESS]]></return_code>'
    '<return_msg><![CDATA[OK]]></return_msg></xml>'
)
PAY_NOTIFY_FAIL_XML = (
    '<xml><return_code><![CDATA[FAIL]]></return_code>'
    '<return_msg><![CDATA[FAIL]]></return_msg></xml>'
)


def quit_records_no_show(previous_state, invite_success_state):
    """已经约上后再取消，这一对定金立刻结算。只是撤回自己的邀请不算。"""
    return previous_state == invite_success_state


def format_out_trade_no(order_id):
    return '%s%0*d' % (OUT_TRADE_NO_PREFIX, OUT_TRADE_NO_WIDTH, order_id)


def format_out_refund_no(order_id):
    return '%s%0*d' % (OUT_REFUND_NO_PREFIX, OUT_TRADE_NO_WIDTH, order_id)
