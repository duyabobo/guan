#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""注册短信验证码。Redis 只短时保存，日志不记号码和验证码。"""
import logging

from service.common.phone_number import (
    PHONE_CODE_KEY,
    PHONE_CODE_RESEND_SEC,
    PHONE_CODE_TTL_SEC,
    PHONE_GAP_NUMBER_KEY,
    PHONE_GAP_PASSPORT_KEY,
    bind_code,
    bind_code_text,
    mainland_mobile,
    new_bind_code,
    same_bind_code,
    saved_token,
)
from util.encode import md5_hex
from util.redis_conn import decode_redis_value, redisConn
from util.sms_gateway import post_messages, sms_configured

logger = logging.getLogger(__name__)


class PhoneCodeService(object):

    def send(self, passport_id, raw_phone):
        number = mainland_mobile(raw_phone)
        if not passport_id or not number:
            logger.info("验证码未发出 passport=%s", passport_id)
            return 'invalid'
        if not sms_configured():
            logger.info("验证码未发出 passport=%s 未配置短信", passport_id)
            return 'unconfigured'
        if not _reserve_gap(passport_id, number):
            logger.info("验证码发送过快 passport=%s", passport_id)
            return 'soon'
        code = new_bind_code()
        sent = post_messages([{'phone': number, 'text': bind_code_text(code)}])
        if not sent:
            _release_gap(passport_id, number)
            logger.info("验证码发送失败 passport=%s", passport_id)
            return 'unconfigured'
        redisConn.set(PHONE_CODE_KEY % passport_id, saved_token(number, code), ex=PHONE_CODE_TTL_SEC)
        logger.info("验证码已发出 passport=%s", passport_id)
        return ''

    def take(self, passport_id, raw_phone, raw_code):
        number = mainland_mobile(raw_phone)
        code = bind_code(raw_code)
        if not passport_id or not number or not code:
            logger.info("验证码不正确 passport=%s", passport_id)
            return ''
        key = PHONE_CODE_KEY % passport_id
        saved = decode_redis_value(redisConn.get(key))
        if not same_bind_code(saved, number, code):
            logger.info("验证码不正确 passport=%s", passport_id)
            return ''
        redisConn.delete(key)
        return number


def _reserve_gap(passport_id, number):
    passport_key = PHONE_GAP_PASSPORT_KEY % passport_id
    number_key = PHONE_GAP_NUMBER_KEY % md5_hex(number)
    if not redisConn.set(passport_key, 1, nx=True, ex=PHONE_CODE_RESEND_SEC):
        return False
    if not redisConn.set(number_key, 1, nx=True, ex=PHONE_CODE_RESEND_SEC):
        redisConn.delete(passport_key)
        return False
    return True


def _release_gap(passport_id, number):
    redisConn.delete(PHONE_GAP_PASSPORT_KEY % passport_id)
    redisConn.delete(PHONE_GAP_NUMBER_KEY % md5_hex(number))
