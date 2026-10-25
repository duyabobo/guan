#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""注册短信验证码。Redis 只短时保存，日志不记号码和验证码。"""
import logging

from service.identity.runtime_key import material_for
from service.common.phone_number import (
    PHONE_CODE_KEY,
    PHONE_CODE_MAX_TRIES,
    PHONE_CODE_RESEND_SEC,
    PHONE_CODE_TTL_SEC,
    PHONE_GAP_NUMBER_KEY,
    PHONE_GAP_PASSPORT_KEY,
    PHONE_TRY_KEY,
    bind_code,
    bind_code_text,
    mainland_mobile,
    new_bind_code,
    same_bind_code,
    saved_token,
)
from util.const.identity import PURPOSE_PHONE_CODE
from util.encode import md5_hex
from util.redis_conn import decode_redis_value, redisConn
from util.sensitive_cipher import decrypt, encrypt, pack_token, unpack_token
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
        if not _store_token(passport_id, number, code):
            _release_gap(passport_id, number)
            return 'invalid'
        redisConn.delete(PHONE_TRY_KEY % passport_id)  # 新验证码重新计试错次数
        logger.info("验证码已发出 passport=%s", passport_id)
        return ''

    def take(self, passport_id, raw_phone, raw_code):
        number = mainland_mobile(raw_phone)
        code = bind_code(raw_code)
        if not passport_id or not number or not code:
            logger.info("验证码不正确 passport=%s", passport_id)
            return ''
        if _tries_exhausted(passport_id):
            return ''
        saved = _load_token(passport_id)
        if not same_bind_code(saved, number, code):
            logger.info("验证码不正确 passport=%s", passport_id)
            return ''
        redisConn.delete(PHONE_CODE_KEY % passport_id, PHONE_TRY_KEY % passport_id)
        return number


def _tries_exhausted(passport_id):
    """验证码只有 6 位，必须限制试错次数，否则可以在有效期内枚举。超限后作废验证码。"""
    try_key = PHONE_TRY_KEY % passport_id
    pipe = redisConn.pipeline()
    pipe.incr(try_key)
    pipe.expire(try_key, PHONE_CODE_TTL_SEC)
    tries, _ = pipe.execute()
    if tries <= PHONE_CODE_MAX_TRIES:
        return False
    redisConn.delete(PHONE_CODE_KEY % passport_id)
    logger.warning("验证码试错次数超限，已作废 passport=%s tries=%s", passport_id, tries)
    return True


def _store_token(passport_id, number, code):
    material = material_for(passport_id, PURPOSE_PHONE_CODE)
    if not material:
        logger.info("验证码未保存，运行时没有身份密钥 passport=%s", passport_id)
        return False
    nonce, cipher = encrypt(material, saved_token(number, code).encode('utf-8'))
    redisConn.set(PHONE_CODE_KEY % passport_id, pack_token(nonce, cipher), ex=PHONE_CODE_TTL_SEC)
    return True


def _load_token(passport_id):
    material = material_for(passport_id, PURPOSE_PHONE_CODE)
    saved = decode_redis_value(redisConn.get(PHONE_CODE_KEY % passport_id))
    nonce, cipher = unpack_token(saved)
    if not material or not nonce:
        return ''
    try:
        return decrypt(material, nonce, cipher).decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        logger.info("验证码解不开 passport=%s", passport_id)
        return ''


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
