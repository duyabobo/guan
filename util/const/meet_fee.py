#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""单次见面付费。没有爽约时免费。一次爽约之后每次 10 元，两次 20 元，按次数累加。"""

MEET_FEE_STEP_YUAN = 10
FEN_PER_YUAN = 100
NO_SHOW_REVOKE_FREE_AT = 1

FEE_ORDER_CREATED = 0
FEE_ORDER_PAID = 1
FEE_ORDER_CONSUMED = 2
FEE_ORDER_REFUND_PENDING = 3
FEE_ORDER_REFUNDED = 4
FEE_ORDER_CLOSED = 5

FEE_REFUNDABLE_STATUSES = (
    FEE_ORDER_PAID,
    FEE_ORDER_CONSUMED,
    FEE_ORDER_REFUND_PENDING,
)

PREPAY_REUSE_MINUTES = 90
OUT_TRADE_NO_PREFIX = 'MF'
OUT_REFUND_NO_PREFIX = 'MR'
OUT_TRADE_NO_WIDTH = 20
PAY_BODY = '关关雎鸠单次见面'
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


def meet_fee_required(no_show_count):
    """有过一次爽约，免费入座就取消。"""
    return (no_show_count or 0) >= NO_SHOW_REVOKE_FREE_AT


def meet_fee_yuan(no_show_count):
    """一次 10 元，两次 20 元，次数继续往上加。没有爽约时是 0。"""
    count = no_show_count or 0
    if count < NO_SHOW_REVOKE_FREE_AT:
        return 0
    return count * MEET_FEE_STEP_YUAN


def meet_fee_fen(no_show_count):
    return meet_fee_yuan(no_show_count) * FEN_PER_YUAN


def quit_records_no_show(previous_state, invite_success_state):
    """已经约上后再取消，记爽约。只是撤回自己的邀请不算。"""
    return previous_state == invite_success_state


def fee_banner_text(no_show_count):
    return '你有%d次爽约，之后每次见面需要支付%d元' % (no_show_count, meet_fee_yuan(no_show_count))


def fee_confirm_hint(no_show_count):
    return '你有%d次爽约，这次见面需要支付%d元' % (no_show_count, meet_fee_yuan(no_show_count))


def no_show_toast(no_show_count):
    return '已记录第%d次爽约，之后每次见面需要支付%d元' % (no_show_count, meet_fee_yuan(no_show_count))


def no_show_notice_note(no_show_count):
    return '之后每次见面需付%d元' % meet_fee_yuan(no_show_count)


def format_out_trade_no(order_id):
    return '%s%0*d' % (OUT_TRADE_NO_PREFIX, OUT_TRADE_NO_WIDTH, order_id)


def format_out_refund_no(order_id):
    return '%s%0*d' % (OUT_REFUND_NO_PREFIX, OUT_TRADE_NO_WIDTH, order_id)
