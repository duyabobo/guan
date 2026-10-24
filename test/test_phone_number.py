#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from service.common.phone_number import PHONE_DIGIT_COUNT, mainland_mobile
from util.const.notice import SCENE_MEET_SOON, SCENE_NO_SHOW, notice_sms_text


def test_mainland_mobile_accepts_cn_eleven_digits():
    info = {'countryCode': '86', 'purePhoneNumber': '13800138000'}
    assert mainland_mobile(info) == '13800138000'
    assert len(mainland_mobile(info)) == PHONE_DIGIT_COUNT


def test_mainland_mobile_accepts_numeric_country():
    info = {'countryCode': 86, 'purePhoneNumber': '13800138000'}
    assert mainland_mobile(info) == '13800138000'


def test_mainland_mobile_rejects_other_country_and_short_number():
    assert mainland_mobile({'countryCode': '1', 'purePhoneNumber': '13800138000'}) == ''
    assert mainland_mobile({'countryCode': '86', 'purePhoneNumber': '1380013800'}) == ''
    assert mainland_mobile(None) == ''


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
