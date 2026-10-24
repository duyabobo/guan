#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from service.common.phone_number import (
    PHONE_CODE_LENGTH,
    PHONE_CODE_TTL_MINUTES,
    PHONE_DIGIT_COUNT,
    bind_code,
    bind_code_text,
    mainland_mobile,
    new_bind_code,
    redact_phone_body,
    same_bind_code,
    saved_token,
)
from util.const.notice import SCENE_MEET_SOON, SCENE_NO_SHOW, notice_sms_text


def test_mainland_mobile_accepts_eleven_digits():
    assert mainland_mobile('13800138000') == '13800138000'
    assert len(mainland_mobile('13800138000')) == PHONE_DIGIT_COUNT


def test_mainland_mobile_rejects_short_and_empty():
    assert mainland_mobile('1380013800') == ''
    assert mainland_mobile('') == ''
    assert mainland_mobile(None) == ''


def test_bind_code_text_is_only_the_code():
    text = bind_code_text('123456')
    assert '123456' in text
    assert ('%s分钟' % PHONE_CODE_TTL_MINUTES) in text
    assert '通知' not in text


def test_bind_code_roundtrip():
    code = new_bind_code()
    assert len(code) == PHONE_CODE_LENGTH
    assert code.isdigit()
    assert bind_code(code) == code
    assert bind_code('12345') == ''
    saved = saved_token('13800138000', code)
    wrong = '000001' if code == '000000' else '000000'
    assert same_bind_code(saved, '13800138000', code)
    assert not same_bind_code(saved, '13800138000', wrong)
    assert not same_bind_code(saved, '13800138001', code)


def test_phone_body_log_keeps_length_only():
    body = {'phone': '13800138000', 'code': ['123456'], 'requestSeq': 'abc'}
    logged = redact_phone_body('/phone', body)
    assert logged['phone'] == PHONE_DIGIT_COUNT
    assert logged['code'] == PHONE_CODE_LENGTH
    assert logged['requestSeq'] == 'abc'
    assert '13800138000' not in str(logged)


def test_sms_meet_soon_uses_boss_greeting():
    ten = datetime.datetime(2026, 10, 24, 10, 0)
    half = datetime.datetime(2026, 10, 24, 10, 30)
    assert '你好老板，我十点约了人' in notice_sms_text(SCENE_MEET_SOON, ten)
    assert '你好老板，我十点半约了人' in notice_sms_text(SCENE_MEET_SOON, half)


def test_sms_uses_passed_note():
    start = datetime.datetime(2026, 10, 24, 10, 0)
    text = notice_sms_text(SCENE_NO_SHOW, start, '之后每次见面 20 元')
    assert '之后每次见面 20 元' in text
    assert '已记录爽约' in text
