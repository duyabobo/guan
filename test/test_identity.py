#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.identity.assertion import IdentityAssertion
from service.identity.registry import get_provider
from service.identity.wechat_session import parse_wechat_session
from service.sensitive.purpose import purpose_accepted
from util.const.identity import PROVIDER_NATIONAL_NETWORK, PROVIDER_WECHAT
from util.session_payload import session_payload


def test_session_has_no_identity_secret():
    payload = session_payload(7, 'sign-secret')
    assert set(payload) == {'secret', 'id'}
    assert payload['id'] == 7


def test_parse_wechat_session_drops_session_key():
    item = parse_wechat_session({
        'openid': 'openid-1',
        'unionid': 'union-secret',
        'session_key': 'session-key',
    })
    assert item.provider == PROVIDER_WECHAT
    assert item.account_key == 'openid-1'
    assert item.secret_material == 'union-secret'
    assert 'union-secret' not in repr(item)
    assert 'session-key' not in repr(item)
    assert 'openid-1' not in repr(item)


def test_parse_uses_openid_when_unionid_missing():
    item = parse_wechat_session({'openid': 'openid-1'})
    assert item.provider == PROVIDER_WECHAT
    assert item.account_key == 'openid-1'
    assert item.secret_material == 'openid-1'


def test_parse_rejects_incomplete_session():
    assert parse_wechat_session({'errcode': 40029, 'errmsg': 'invalid code'}) is None
    assert parse_wechat_session({}) is None
    assert parse_wechat_session(None) is None


def test_assertion_repr_hides_secret():
    item = IdentityAssertion(PROVIDER_WECHAT, 'openid-1', 'union-secret')
    assert repr(item) == 'IdentityAssertion(provider=%s)' % PROVIDER_WECHAT


def test_unknown_provider_rejected():
    assert PROVIDER_NATIONAL_NETWORK != PROVIDER_WECHAT
    assert get_provider('unknown') is None


def test_reveal_requires_purpose():
    assert purpose_accepted('') is False
    assert purpose_accepted('查') is False
    assert purpose_accepted('协助核查原始语音') is True
