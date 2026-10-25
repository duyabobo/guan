#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""微信 HTTP。只记录路径和结果码，不记录 token、密钥和 openid。"""
import json
import logging
from urllib import request as urlrequest

logger = logging.getLogger(__name__)


def path_of(url):
    return (url or '').split('?', 1)[0]


def read_json(url, timeout):
    logger.info("请求微信 path=%s", path_of(url))
    req = urlrequest.Request(url)
    with urlrequest.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def post_json(url, payload, timeout):
    logger.info("请求微信 path=%s", path_of(url))
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urlrequest.Request(url, data=body, headers={'Content-Type': 'application/json'})
    with urlrequest.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))
