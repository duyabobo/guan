#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.log_redact import redact_body, redact_uri, summarize_for_log
from util.session_payload import session_payload
from util.slot_blind import activity_slot_key


def test_session_still_has_no_unionid():
    payload = session_payload(7, 'sign-secret')
    assert 'unionid' not in payload
    assert set(payload) == {'secret', 'id'}


def test_slot_key_does_not_reveal_activity_id():
    pepper = 'test-pepper'
    first = activity_slot_key(18, pepper)
    second = activity_slot_key(18, pepper)
    other = activity_slot_key(19, pepper)
    assert first == second
    assert first != other
    assert len(first) == 64
    assert first != '18'
    assert activity_slot_key(0, pepper) == ''


def test_log_hides_login_code_and_phone():
    uri = redact_uri('/login?code=abc123&shareOpenid=xx')
    assert 'abc123' not in uri
    assert 'code=6' in uri
    body = redact_body({'phone': '13800138000', 'voiceText': '我今年二十八', 'requestSeq': 's'})
    assert body['requestSeq'] == 's'
    assert '13800138000' not in str(body)
    assert '二十八' not in str(body)
    logged = summarize_for_log([{'address': '三里屯', 'time': '10:00'}])
    assert logged == {'count': 1}
    assert '三里屯' not in str(logged)
