#! /usr/bin/env python
# -*- coding: utf-8 -*-
import http.client
import json
import logging
import socket
import time
from urllib import parse as urlparse

from tornado import gen
from tornado.ioloop import IOLoop

import util.config
from util.const.mini_program import WX_API_HOST
from util.const.mini_program import WX_MINIPROGRAM_CODE_TO_SESSION

logger = logging.getLogger(__name__)

CODE_TO_SESSION_TIMEOUT = 8
CONNECT_TIMEOUT_SECONDS = 2
HTTPS_PORT = 443
HTTP_STATUS_OK = 200


class WxHelper(object):
    def __init__(self):
        self.appid = util.config.get("weixin", "appid")
        self.secret = util.config.get("weixin", "secret")

    @gen.coroutine
    def codeToSession(self, js_code):
        """向微信换登录态。同一个域名有多个地址，一个丢包就换下一个。"""
        if not js_code:
            logger.warning("微信 code 为空")
            raise gen.Return({})
        path = _session_path({
            'js_code': js_code,
            'appid': self.appid,
            'secret': self.secret,
            'grant_type': 'authorization_code',
        })
        payload = yield IOLoop.current().run_in_executor(
            None, _fetch_session, path, CODE_TO_SESSION_TIMEOUT)
        raise gen.Return(json.loads(payload) if payload else {})


def _session_path(params):
    path = urlparse.urlparse(WX_MINIPROGRAM_CODE_TO_SESSION).path
    return '{}?{}'.format(path, urlparse.urlencode(params))


def _ipv4_addresses(host):
    found = []
    for item in socket.getaddrinfo(host, HTTPS_PORT, socket.AF_INET, socket.SOCK_STREAM):
        ip = item[4][0]
        if ip not in found:
            found.append(ip)
    return found


class _AddressPinnedHTTPSConnection(http.client.HTTPSConnection):
    """连指定地址，证书校验仍用域名。"""

    def __init__(self, hostname, ip, timeout):
        super().__init__(hostname, HTTPS_PORT, timeout=timeout)
        self._ip = ip

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def _request_one(ip, path, timeout):
    connection = _AddressPinnedHTTPSConnection(WX_API_HOST, ip, timeout)
    try:
        connection.request('GET', path)
        response = connection.getresponse()
        payload = response.read()
        if response.status != HTTP_STATUS_OK:
            raise http.client.HTTPException('status=%s' % response.status)
        return payload
    finally:
        connection.close()


def _fetch_session(path, timeout):
    addresses = _ipv4_addresses(WX_API_HOST)
    if not addresses:
        raise socket.gaierror(WX_API_HOST)
    deadline = time.time() + timeout
    last_error = TimeoutError('wechat connect timed out')
    for ip in addresses:
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        attempt_timeout = CONNECT_TIMEOUT_SECONDS if remaining > CONNECT_TIMEOUT_SECONDS else remaining
        try:
            return _request_one(ip, path, attempt_timeout)
        except (TimeoutError, socket.timeout, OSError, http.client.HTTPException) as exc:
            last_error = exc
            logger.warning("微信地址连接失败 ip=%s err=%s", ip, type(exc).__name__)
    raise last_error
