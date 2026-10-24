#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""微信支付 v2。签名和组包不访问网络。"""
import hashlib
import logging
import xml.etree.ElementTree as ET

from util.const.meet_fee import WX_SIGN_TYPE_MD5, WX_SUCCESS
from util.wx_http import post_xml

logger = logging.getLogger(__name__)

_UNIFIED_ORDER_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
_ORDER_QUERY_URL = 'https://api.mch.weixin.qq.com/pay/orderquery'
_REFUND_URL = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
_SIGN_KEYS = ('sign', 'paySign')


def sign_v2(params, api_key):
    pieces = []
    for key in sorted(params):
        if key in _SIGN_KEYS:
            continue
        value = params.get(key)
        if value is None or value == '':
            continue
        pieces.append('%s=%s' % (key, value))
    pieces.append('key=%s' % api_key)
    raw = '&'.join(pieces).encode('utf-8')
    return hashlib.md5(raw).hexdigest().upper()


def client_pay_params(prepay_id, appid, api_key, timestamp, nonce):
    signed = {
        'appId': appid,
        'timeStamp': str(timestamp),
        'nonceStr': nonce,
        'package': 'prepay_id=%s' % prepay_id,
        'signType': WX_SIGN_TYPE_MD5,
    }
    signed['paySign'] = sign_v2(signed, api_key)
    return {
        'timeStamp': signed['timeStamp'],
        'nonceStr': signed['nonceStr'],
        'package': signed['package'],
        'signType': signed['signType'],
        'paySign': signed['paySign'],
    }


def dict_to_xml(data):
    parts = ['<xml>']
    for key, value in data.items():
        parts.append('<%s><![CDATA[%s]]></%s>' % (key, value, key))
    parts.append('</xml>')
    return ''.join(parts)


def parse_xml(raw):
    if isinstance(raw, bytes):
        text = raw.decode('utf-8')
    else:
        text = raw or ''
    root = ET.fromstring(text)
    parsed = {}
    for child in list(root):
        parsed[child.tag] = child.text or ''
    return parsed


def xml_succeeded(parsed):
    return parsed.get('return_code') == WX_SUCCESS and parsed.get('result_code') == WX_SUCCESS


def sign_matches(parsed, api_key):
    if not api_key or not parsed.get('sign'):
        return False
    return parsed.get('sign') == sign_v2(parsed, api_key)


def unified_order(params, api_key, timeout):
    payload = dict(params)
    payload['sign'] = sign_v2(payload, api_key)
    raw = post_xml(_UNIFIED_ORDER_URL, dict_to_xml(payload), timeout)
    parsed = parse_xml(raw)
    logger.info(
        "微信下单 return=%s result=%s err=%s",
        parsed.get('return_code'), parsed.get('result_code'), parsed.get('err_code'),
    )
    if not xml_succeeded(parsed) or not parsed.get('prepay_id'):
        return ''
    return parsed.get('prepay_id')


def query_order(params, api_key, timeout):
    payload = dict(params)
    payload['sign'] = sign_v2(payload, api_key)
    raw = post_xml(_ORDER_QUERY_URL, dict_to_xml(payload), timeout)
    parsed = parse_xml(raw)
    logger.info(
        "微信查单 return=%s result=%s trade=%s err=%s",
        parsed.get('return_code'), parsed.get('result_code'),
        parsed.get('trade_state'), parsed.get('err_code'),
    )
    return parsed


def refund_order(params, api_key, timeout, cert_file, key_file):
    payload = dict(params)
    payload['sign'] = sign_v2(payload, api_key)
    raw = post_xml(_REFUND_URL, dict_to_xml(payload), timeout, cert_file, key_file)
    parsed = parse_xml(raw)
    logger.info(
        "微信退款 return=%s result=%s err=%s",
        parsed.get('return_code'), parsed.get('result_code'), parsed.get('err_code'),
    )
    return xml_succeeded(parsed)
