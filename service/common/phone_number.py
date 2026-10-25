#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""大陆手机号和短信验证码。只做格式，不访问 Redis，也不落库。"""
import hmac
import secrets

PHONE_DIGIT_COUNT = 11
PHONE_CODE_LENGTH = 6
PHONE_CODE_TTL_MINUTES = 5
PHONE_CODE_TTL_SEC = PHONE_CODE_TTL_MINUTES * 60
PHONE_CODE_RESEND_SEC = 60
PHONE_CODE_MAX_TRIES = 5  # 一个验证码最多试错次数，超过后验证码作废，必须重新获取
PHONE_CODE_RADIX = 10
PHONE_CODE_KEY = 'phone_bind:%s'
PHONE_GAP_PASSPORT_KEY = 'phone_bind_gap:%s'
PHONE_GAP_NUMBER_KEY = 'phone_bind_gap_n:%s'
PHONE_TRY_KEY = 'phone_bind_try:%s'
PHONE_SAVED_SEP = ':'
PHONE_BIND_PATH = '/phone'
PHONE_CODE_PATH = '/phone_code'
_HIDDEN_LOG_FIELDS = ('phone', 'code')


def mainland_mobile(text):
    number = str(text or '').strip()
    if len(number) != PHONE_DIGIT_COUNT or not number.isdigit():
        return ''
    return number


def bind_code(text):
    code = str(text or '').strip()
    if len(code) != PHONE_CODE_LENGTH or not code.isdigit():
        return ''
    return code


def new_bind_code():
    span = PHONE_CODE_RADIX ** PHONE_CODE_LENGTH
    return '%0*d' % (PHONE_CODE_LENGTH, secrets.randbelow(span))


def bind_code_text(code):
    return '验证码%s，%s分钟内有效' % (code, PHONE_CODE_TTL_MINUTES)


def saved_token(number, code):
    return '%s%s%s' % (number, PHONE_SAVED_SEP, code)


def same_bind_code(saved, number, code):
    saved_number, sep, saved_code = (saved or '').partition(PHONE_SAVED_SEP)
    if not sep or not number or not code:
        return False
    if len(saved_number) != len(number) or len(saved_code) != len(code):
        return False
    number_ok = hmac.compare_digest(saved_number, number)
    code_ok = hmac.compare_digest(saved_code, code)
    return number_ok and code_ok


def redact_phone_body(path, body):
    """请求日志只留手机号和验证码的长度。"""
    if path not in (PHONE_BIND_PATH, PHONE_CODE_PATH) or not isinstance(body, dict):
        return body
    hidden = {}
    for key, value in body.items():
        if key in _HIDDEN_LOG_FIELDS:
            hidden[key] = _field_length(value)
        else:
            hidden[key] = value
    return hidden


def _field_length(value):
    if isinstance(value, (list, tuple)):
        if not value:
            return 0
        value = value[0]
    if isinstance(value, bytes):
        return len(value)
    return len(str(value or ''))
