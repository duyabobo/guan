#! /usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.mock import MagicMock

import pytest

from ral import passport
from util.auth import Checker
from util.errors import RateLimitExceeded, ReplayDetected, RuntimeIdentityMissing, SignatureInvalid
from util.redis_conn import redisConn


def test_success_limit_rejects_and_keeps_rejecting_in_window():
    """超限后窗口内一直拒绝。旧实现超限就清计数，等于每 301 次才拒绝 1 次。"""
    for _ in range(passport.SUCCESS_CNT_LIMIT_ONE_MINUTE + 1):
        passport.setSuccessCnt('token-a')
    for _ in range(3):
        with pytest.raises(RateLimitExceeded):
            passport.checkSuccessCnt('token-a')


def test_success_limit_is_per_subject():
    for _ in range(passport.SUCCESS_CNT_LIMIT_ONE_MINUTE + 1):
        passport.setSuccessCnt('token-a')
    passport.checkSuccessCnt('token-b')


def test_counter_keys_always_expire():
    passport.setSuccessCnt('token-c')
    keys = redisConn.keys('success_cnt:token-c:*')
    assert keys
    assert redisConn.ttl(keys[0]) > 0


def test_failed_limit_blocks_ip():
    for _ in range(passport.FAILED_CNT_LIMIT_ONE_MINUTE):
        passport.setFailCnt('1.2.3.4')
    with pytest.raises(RateLimitExceeded):
        passport.checkFailedCnt('1.2.3.4')
    passport.checkFailedCnt('5.6.7.8')


def test_replay_of_same_request_seq_is_rejected():
    passport.checkUnique('token-d', 'seq-1')
    with pytest.raises(ReplayDetected):
        passport.checkUnique('token-d', 'seq-1')
    passport.checkUnique('token-d', 'seq-2')
    passport.checkUnique('token-e', 'seq-1')


def _handler(access_token='', sign='', passport_id=0, secret=''):
    handler = MagicMock()
    handler.request.remote_ip = '9.9.9.9'
    handler.request.path = '/guanguan'
    handler.request.method = 'GET'
    handler.request.query = ''
    handler.request.body = b''
    handler.request.headers = {}
    handler.request.arguments = {}
    handler.requestSeq = 'seq'
    handler.accessToken = access_token
    handler.sign = sign
    handler.currentPassport = {'id': passport_id, 'secret': secret}
    return handler


def test_checker_counts_by_access_token_not_shared_empty_key():
    """会话里没有 accessToken 字段。计数键必须取请求带来的令牌，否则所有用户共用一个计数。"""
    assert Checker(_handler(access_token='tok-1')).rate_subject == 'tok-1'


def test_checker_counts_anonymous_requests_by_ip():
    assert Checker(_handler(access_token='')).rate_subject == 'ip:9.9.9.9'


def test_checker_rejects_bad_signature():
    checker = Checker(_handler(access_token='tok', sign='not-the-digest', secret='s'))
    with pytest.raises(SignatureInvalid):
        checker.check_sign('s')


def test_checker_rejects_missing_signature():
    checker = Checker(_handler(access_token='tok', sign=None, secret='s'))
    with pytest.raises(SignatureInvalid):
        checker.check_sign('s')


def test_checker_requires_runtime_identity_for_logged_in_user():
    checker = Checker(_handler(access_token='tok', passport_id=42))
    with pytest.raises(RuntimeIdentityMissing):
        checker.require_runtime_key()
