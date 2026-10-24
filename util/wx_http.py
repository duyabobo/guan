#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""微信 HTTP。只记录路径和结果码，不记录 token、密钥和 openid。"""
import json
import logging
import ssl
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


def post_xml(url, xml_text, timeout, cert_file='', key_file=''):
    logger.info("请求微信 path=%s", path_of(url))
    req = urlrequest.Request(
        url,
        data=xml_text.encode('utf-8'),
        headers={'Content-Type': 'text/xml'},
    )
    context = None
    if cert_file and key_file:
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    with urlrequest.urlopen(req, timeout=timeout, context=context) as resp:
        return resp.read()
