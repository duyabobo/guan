#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""请求签名拼接。算法与 miniprogram/util/request.js 的 getContentFromQuery 一致。"""
import base64
import json
from urllib import parse as urlparse

from util.encode import md5_hex

SIGN_FIELD_SEP = "|"
SKIP_VALUE = "undefined"
MULTIPART_CONTENT = "multipart/form-data"


def encode_text(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    return base64.b64encode(str(text).encode("utf-8")).decode("ascii")


def content_from_query(data, sep=SIGN_FIELD_SEP):
    if isinstance(data, str):
        return encode_text(data)
    if isinstance(data, (int, float)):
        return encode_text(str(data))
    if isinstance(data, dict):
        parts = [
            content_from_query(key, sep) + sep + content_from_query(value, sep)
            for key, value in sorted(data.items(), key=lambda item: item[0])
        ]
        return sep.join(parts)
    if isinstance(data, list):
        parts = [
            content_from_query(index, sep) + sep + content_from_query(data[index], sep)
            for index in range(len(data))
        ]
        return sep.join(parts)
    return ""


def form_fields(form_arguments):
    """文件本体不在 arguments 里，这里只签文本字段。"""
    fields = {}
    for key, values in (form_arguments or {}).items():
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        if not values:
            continue
        value = values[0]
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        fields[key] = value
    return fields


def collect_params(path, method, secret, body, query, content_type, form_arguments):
    params = {"secret": secret, "path": path, "method": method}
    if content_type and MULTIPART_CONTENT in content_type:
        params.update(form_fields(form_arguments))
    elif body:
        params.update(json.loads(body))
    if query:
        params.update(dict(urlparse.parse_qsl(query, keep_blank_values=1)))
    return {key: value for key, value in params.items() if value != SKIP_VALUE}


def sign_digest(path, method, secret, body, query, content_type="", form_arguments=None):
    params = collect_params(path, method, secret, body, query, content_type, form_arguments)
    return md5_hex(content_from_query(params))
