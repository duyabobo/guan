#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""阿里云国内短信。验证码走 SendSms，活动提醒走 SendBatchSms。日志不记号码和验证码。"""
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from util.config import get_conf

logger = logging.getLogger(__name__)

API_HOST = 'dysmsapi.aliyuncs.com'
API_VERSION = '2017-05-25'
SIGN_ALGORITHM = 'ACS3-HMAC-SHA256'
ACTION_SEND = 'SendSms'
ACTION_BATCH = 'SendBatchSms'
SMS_OK = 'OK'
SMS_BATCH_LIMIT = 100
SMS_HTTP_TIMEOUT_SEC = 5
EMPTY_PAYLOAD_HASH = hashlib.sha256(b'').hexdigest()
PARAM_CODE = 'code'
PARAM_TITLE = 'title'
PARAM_WHEN = 'when'
PARAM_NOTE = 'note'
_SECTION = 'aliyun_sms'
_KEY_ID = 'aliyun_sms_access_key_id'
_KEY_SECRET = 'aliyun_sms_access_key_secret'
_SIGN_NAME = 'aliyun_sms_sign_name'
_VERIFY_TEMPLATE = 'aliyun_sms_verify_template_code'
_NOTICE_TEMPLATE = 'aliyun_sms_notice_template_code'
_SIGNED_HEADER_NAMES = (
    'host',
    'x-acs-action',
    'x-acs-content-sha256',
    'x-acs-date',
    'x-acs-signature-nonce',
    'x-acs-version',
)


def verify_configured():
    return _ready(_VERIFY_TEMPLATE)


def notice_configured():
    return _ready(_NOTICE_TEMPLATE)


def send_verify_code(phone, code):
    if not verify_configured() or not phone or not code:
        return False
    query = {
        'PhoneNumbers': phone,
        'SignName': _conf(_SIGN_NAME),
        'TemplateCode': _conf(_VERIFY_TEMPLATE),
        'TemplateParam': _json({PARAM_CODE: code}),
    }
    return _call(ACTION_SEND, query, 1)


def send_notices(items):
    """同一通知模板，按阿里云单次 100 个号码分批。返回实际受理的那些条目。"""
    if not notice_configured():
        return []
    ready = [item for item in items if item.get('phone')]
    sign_name = _conf(_SIGN_NAME)
    template = _conf(_NOTICE_TEMPLATE)
    sent = []
    for chunk in _chunks(ready, SMS_BATCH_LIMIT):
        if _send_chunk(chunk, sign_name, template):
            sent.extend(chunk)
    return sent


def build_signed_request(action, version, host, query, key_id, secret, nonce, stamp):
    """按阿里云 V3 签名拼出 POST 地址和请求头。query 的值保持原文。"""
    headers = {
        'host': host,
        'x-acs-action': action,
        'x-acs-content-sha256': EMPTY_PAYLOAD_HASH,
        'x-acs-date': stamp,
        'x-acs-signature-nonce': nonce,
        'x-acs-version': version,
    }
    canonical_headers = ''.join('%s:%s\n' % (name, headers[name]) for name in _SIGNED_HEADER_NAMES)
    signed_names = ';'.join(_SIGNED_HEADER_NAMES)
    canonical = '\n'.join((
        'POST',
        '/',
        _query(query),
        canonical_headers,
        signed_names,
        EMPTY_PAYLOAD_HASH,
    ))
    string_to_sign = SIGN_ALGORITHM + '\n' + _sha256_hex(canonical.encode('utf-8'))
    signature = hmac.new(
        secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256,
    ).hexdigest()
    headers['authorization'] = '%s Credential=%s,SignedHeaders=%s,Signature=%s' % (
        SIGN_ALGORITHM, key_id, signed_names, signature,
    )
    return 'https://%s/?%s' % (host, _query(query)), headers


def _ready(template_key):
    return bool(_conf(_KEY_ID) and _conf(_KEY_SECRET) and _conf(_SIGN_NAME) and _conf(template_key))


def _conf(name):
    return get_conf(name, '', _SECTION).strip()


def _send_chunk(chunk, sign_name, template):
    query = {
        'PhoneNumberJson': _json([item['phone'] for item in chunk]),
        'SignNameJson': _json([sign_name] * len(chunk)),
        'TemplateCode': template,
        'TemplateParamJson': _json([
            {PARAM_TITLE: item['title'], PARAM_WHEN: item['when'], PARAM_NOTE: item['note']}
            for item in chunk
        ]),
    }
    return _call(ACTION_BATCH, query, len(chunk))


def _call(action, query, count):
    url, headers = build_signed_request(
        action, API_VERSION, API_HOST, query,
        _conf(_KEY_ID), _conf(_KEY_SECRET), uuid.uuid4().hex,
        datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    )
    payload = _open(url, headers)
    request_id = payload.get('RequestId', '')
    if payload.get('Code') == SMS_OK:
        logger.info('阿里云短信已受理 action=%s count=%s request=%s', action, count, request_id)
        return True
    logger.warning(
        '阿里云短信未受理 action=%s count=%s code=%s request=%s',
        action, count, payload.get('Code') or 'empty', request_id,
    )
    return False


def _open(url, headers):
    request = Request(url, data=b'', method='POST')
    request.remove_header('Content-type')
    for name, value in headers.items():
        request.add_header(name, value)
    try:
        with urlopen(request, timeout=SMS_HTTP_TIMEOUT_SEC) as response:
            raw = response.read()
    except HTTPError as exc:
        raw = exc.read()
    except (URLError, TimeoutError, OSError) as exc:
        logger.warning('阿里云短信请求失败 %s', type(exc).__name__)
        return {}
    return _json_body(raw)


def _json_body(raw):
    try:
        payload = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.warning('阿里云短信返回不是 JSON')
        return {}
    if not isinstance(payload, dict):
        logger.warning('阿里云短信返回不是对象')
        return {}
    return payload


def _chunks(items, size):
    return [items[index:index + size] for index in range(0, len(items), size)]


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _query(params):
    return '&'.join(
        '%s=%s' % (_percent(key), _percent(params[key])) for key in sorted(params)
    )


def _percent(value):
    encoded = quote(str(value), safe='')
    return encoded.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')


def _sha256_hex(raw):
    return hashlib.sha256(raw).hexdigest()
