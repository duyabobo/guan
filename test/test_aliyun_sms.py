#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from contextlib import contextmanager
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from util.aliyun_sms import (
    ACTION_BATCH,
    ACTION_SEND,
    SMS_BATCH_LIMIT,
    build_signed_request,
    notice_configured,
    send_notices,
    send_verify_code,
    verify_configured,
)

_ENV_KEYS = (
    'ALIYUN_SMS_ACCESS_KEY_ID',
    'ALIYUN_SMS_ACCESS_KEY_SECRET',
    'ALIYUN_SMS_SIGN_NAME',
    'ALIYUN_SMS_VERIFY_TEMPLATE_CODE',
    'ALIYUN_SMS_NOTICE_TEMPLATE_CODE',
)
_SAMPLE_SIGNATURE = '06563a9e1b43f5dfe96b81484da74bceab24a1d853912eee15083a6f0f3283c0'


@contextmanager
def _sms_env():
    previous = {key: os.environ.get(key) for key in _ENV_KEYS}
    os.environ['ALIYUN_SMS_ACCESS_KEY_ID'] = 'test-id'
    os.environ['ALIYUN_SMS_ACCESS_KEY_SECRET'] = 'test-secret'
    os.environ['ALIYUN_SMS_SIGN_NAME'] = '关关'
    os.environ['ALIYUN_SMS_VERIFY_TEMPLATE_CODE'] = 'SMS_VERIFY'
    os.environ['ALIYUN_SMS_NOTICE_TEMPLATE_CODE'] = 'SMS_NOTICE'
    try:
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _clear_sms_env():
    previous = {key: os.environ.get(key) for key in _ENV_KEYS}
    for key in _ENV_KEYS:
        os.environ.pop(key, None)
    return previous


def _restore_sms_env(previous):
    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


class _Body(object):
    def __init__(self, raw):
        self.raw = raw

    def read(self):
        return self.raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_signature_matches_aliyun_v3_sample():
    url, headers = build_signed_request(
        action='RunInstances',
        version='2014-05-26',
        host='ecs.cn-shanghai.aliyuncs.com',
        query={
            'ImageId': 'win2019_1809_x64_dtc_zh-cn_40G_alibase_20230811.vhd',
            'RegionId': 'cn-shanghai',
        },
        key_id='YourAccessKeyId',
        secret='YourAccessKeySecret',
        nonce='3156853299f313e23d1673dc12e1703d',
        stamp='2023-10-26T10:22:32Z',
    )
    assert url.endswith(
        '/?ImageId=win2019_1809_x64_dtc_zh-cn_40G_alibase_20230811.vhd&RegionId=cn-shanghai'
    )
    assert headers['authorization'].endswith('Signature=%s' % _SAMPLE_SIGNATURE)
    assert 'YourAccessKeySecret' not in url
    assert 'YourAccessKeySecret' not in headers['authorization']


def test_missing_config_does_not_call_aliyun():
    previous = _clear_sms_env()
    try:
        assert verify_configured() is False
        assert notice_configured() is False
        with patch('util.aliyun_sms.urlopen') as opened:
            assert send_verify_code('13800138000', '123456') is False
            assert send_notices([_notice('13800138000')]) == []
        opened.assert_not_called()
    finally:
        _restore_sms_env(previous)


def test_verify_only_sends_the_code_variable():
    with _sms_env():
        with patch('util.aliyun_sms.urlopen', return_value=_Body(_ok())) as opened:
            assert send_verify_code('13800138000', '123456') is True
    request = opened.call_args.args[0]
    assert request.get_header('X-acs-action') == ACTION_SEND
    query = request.full_url
    assert 'SMS_VERIFY' in query
    assert 'test-secret' not in query
    assert _decoded_template_param(query) == {'code': '123456'}


def test_aliyun_error_code_is_failure():
    with _sms_env():
        body = b'{"Code":"isv.BUSINESS_LIMIT_CONTROL","RequestId":"req-limit"}'
        with patch('util.aliyun_sms.urlopen', return_value=_Body(body)):
            assert send_verify_code('13800138000', '123456') is False


def test_network_error_is_failure():
    with _sms_env():
        with patch('util.aliyun_sms.urlopen', side_effect=URLError('down')):
            assert send_verify_code('13800138000', '123456') is False


def test_http_error_body_is_read():
    with _sms_env():
        error = HTTPError(
            'https://dysmsapi.aliyuncs.com/', 400, 'bad', {},
            BytesIO(b'{"Code":"SignatureDoesNotMatch","RequestId":"req-sign"}'),
        )
        with patch('util.aliyun_sms.urlopen', side_effect=error):
            assert send_verify_code('13800138000', '123456') is False


def test_notice_batch_splits_at_aliyun_limit():
    items = [_notice('1380013%04d' % index) for index in range(SMS_BATCH_LIMIT + 1)]
    with _sms_env():
        with patch('util.aliyun_sms.urlopen', return_value=_Body(_ok())) as opened:
            sent = send_notices(items)
    assert opened.call_count == 2
    assert sent == items
    first = opened.call_args_list[0].args[0]
    assert first.get_header('X-acs-action') == ACTION_BATCH
    assert 'SMS_NOTICE' in first.full_url


def test_failed_batch_does_not_drop_the_next_batch():
    items = [_notice('1380013%04d' % index) for index in range(SMS_BATCH_LIMIT + 1)]
    answers = [
        _Body(b'{"Code":"isv.MOBILE_NUMBER_ILLEGAL","RequestId":"bad"}'),
        _Body(_ok()),
    ]
    with _sms_env():
        with patch('util.aliyun_sms.urlopen', side_effect=answers):
            sent = send_notices(items)
    assert sent == items[SMS_BATCH_LIMIT:]


def test_blank_phone_is_not_sent():
    with _sms_env():
        with patch('util.aliyun_sms.urlopen') as opened:
            assert send_notices([{'phone': '', 'title': 'a', 'when': 'b', 'note': 'c'}]) == []
        opened.assert_not_called()


def _notice(phone):
    return {'phone': phone, 'title': '活动时间快到了', 'when': '11月07日 10:00', 'note': '你好老板，我十点约了人'}


def _ok():
    return b'{"Code":"OK","RequestId":"req-ok"}'


def _decoded_template_param(url):
    from urllib.parse import parse_qs, urlsplit
    values = parse_qs(urlsplit(url).query)['TemplateParam']
    return json.loads(values[0])
