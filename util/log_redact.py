#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""请求日志去掉登录码、令牌、手机号和语音文本。"""
import json
from urllib import parse as urlparse

_HIDDEN_KEYS = ('phone', 'code', 'secret', 'accesstoken', 'voicetext', 'openid', 'unionid', 'sign')


def redact_uri(uri):
    parts = urlparse.urlsplit(uri or '')
    pairs = urlparse.parse_qsl(parts.query, keep_blank_values=True)
    query = urlparse.urlencode([(key, _hidden_or_value(key, value)) for key, value in pairs])
    return urlparse.urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def summarize_for_log(data):
    """响应日志只留规模，不留资料、手机号、语音和见面地点。"""
    if isinstance(data, list):
        return {'count': len(data)}
    if isinstance(data, dict):
        logged = {}
        for key, value in data.items():
            if _should_hide(key) or isinstance(value, (list, dict)):
                logged[key] = _size(value)
            else:
                logged[key] = value
        return logged
    return data


def redact_body(body):
    if isinstance(body, dict):
        return _redact_dict(body)
    if isinstance(body, bytes):
        return redact_body(body.decode('utf-8', errors='replace'))
    if isinstance(body, str):
        return _redact_text(body)
    return body


def _redact_text(text):
    try:
        parsed = json.loads(text)
    except ValueError:
        return redact_uri(text) if '?' in text else text
    if isinstance(parsed, dict):
        return _redact_dict(parsed)
    return text


def _redact_dict(body):
    hidden = {}
    for key, value in body.items():
        hidden[key] = _hidden_or_value(key, value)
    return hidden


def _should_hide(key):
    return str(key).lower() in _HIDDEN_KEYS or str(key).lower() in (
        'rows', 'address', 'text', 'longitude', 'latitude', 'starttime', 'time', 'voicetext',
    )


def _size(value):
    if isinstance(value, (list, tuple, dict)):
        return len(value)
    return _length_of(value)


def _hidden_or_value(key, value):
    if str(key).lower() not in _HIDDEN_KEYS:
        return value
    return _length_of(value)


def _length_of(value):
    if isinstance(value, (list, tuple)):
        if not value:
            return 0
        value = value[0]
    if isinstance(value, bytes):
        return len(value)
    return len(str(value or ''))
