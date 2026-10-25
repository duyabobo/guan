#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from service import phone_code
from service.common.phone_number import PHONE_CODE_KEY, PHONE_CODE_MAX_TRIES
from service.phone_code import PhoneCodeService
from util.redis_conn import redisConn

PASSPORT_ID = 7
PHONE = '13800138000'
CODE = '123456'
WRONG_CODE = '000000'


@pytest.fixture
def stored_code(monkeypatch):
    """跳过真实的身份密钥读取，直接存入一个有效验证码。"""
    monkeypatch.setattr(phone_code, 'material_for', lambda passport_id, purpose: 'unionid-material')
    assert phone_code._store_token(PASSPORT_ID, PHONE, CODE)


def test_correct_code_binds_and_clears_token(stored_code):
    assert PhoneCodeService().take(PASSPORT_ID, PHONE, CODE) == PHONE
    assert redisConn.get(PHONE_CODE_KEY % PASSPORT_ID) is None


def test_wrong_codes_exhaust_tries_and_invalidate_the_code(stored_code):
    service = PhoneCodeService()
    for _ in range(PHONE_CODE_MAX_TRIES):
        assert service.take(PASSPORT_ID, PHONE, WRONG_CODE) == ''
    # 第 MAX_TRIES + 1 次，即使是对的验证码也不再接受：验证码已作废
    assert service.take(PASSPORT_ID, PHONE, CODE) == ''
    assert redisConn.get(PHONE_CODE_KEY % PASSPORT_ID) is None


def test_correct_code_within_tries_still_works(stored_code):
    service = PhoneCodeService()
    for _ in range(PHONE_CODE_MAX_TRIES - 1):
        service.take(PASSPORT_ID, PHONE, WRONG_CODE)
    assert service.take(PASSPORT_ID, PHONE, CODE) == PHONE
