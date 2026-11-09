#! /usr/bin/env python
# -*- coding: utf-8 -*-
import http.client
import json
import logging
import random
import socket
import struct
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

DNS_PORT = 53
DNS_QUERY_TIMEOUT = 2
DNS_ID_SPACE = 65536
DNS_HEADER_LEN = 12
DNS_QUESTION_COUNT = 1
DNS_NO_RECORD = 0
DNS_QUESTION_TAIL = 4
DNS_ANSWER_META_LEN = 10
DNS_LABEL_MAX = 63
DNS_NAME_HOPS = 16
DNS_PACKET_LIMIT = 512
DNS_TYPE_A = 1
DNS_CLASS_IN = 1
DNS_FLAG_RECURSION = 0x0100
DNS_FLAG_RESPONSE = 0x8000
DNS_FLAG_TRUNCATED = 0x0200
DNS_RCODE_MASK = 0x000F
DNS_POINTER_MASK = 0xC0
IPV4_OCTETS = 4
PUBLIC_DNS_RESOLVERS = ('223.5.5.5', '119.29.29.29')
ADDRESS_CACHE_SECONDS = 300

_address_cache = {}


class WxHelper(object):
    def __init__(self):
        self.appid = util.config.get("weixin", "appid")
        self.secret = util.config.get("weixin", "secret")

    @gen.coroutine
    def codeToSession(self, js_code):
        """向微信换登录态。解析和连接都算在总超时里，一个地址失败就换下一个。"""
        if not js_code:
            logger.warning("微信 code 为空")
            raise gen.Return({})
        logger.info("开始向微信换登录态")
        path = _session_path({
            'js_code': js_code,
            'appid': self.appid,
            'secret': self.secret,
            'grant_type': 'authorization_code',
        })
        payload = yield IOLoop.current().run_in_executor(
            None, _fetch_session, path, CODE_TO_SESSION_TIMEOUT)
        logger.info("微信登录态已返回")
        raise gen.Return(json.loads(payload) if payload else {})


def _session_path(params):
    path = urlparse.urlparse(WX_MINIPROGRAM_CODE_TO_SESSION).path
    return '{}?{}'.format(path, urlparse.urlencode(params))


def _fetch_session(path, timeout):
    deadline = time.time() + timeout
    addresses = _addresses_for(WX_API_HOST, deadline)
    if not addresses:
        raise socket.gaierror(WX_API_HOST)
    return _request_until(addresses, path, deadline)


def _request_until(addresses, path, deadline):
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
    _drop_address_cache(WX_API_HOST)
    raise last_error


def _addresses_for(host, deadline):
    cached = _cached_addresses(host, time.time())
    if cached:
        return cached
    remaining = deadline - time.time()
    if remaining <= 0:
        return []
    found = _resolve_ipv4(host, remaining)
    if found:
        _store_addresses(host, found, time.time())
        logger.info("微信地址已解析 count=%s", len(found))
    return found


def _cached_addresses(host, now):
    item = _address_cache.get(host)
    if not item or item[0] <= now:
        return None
    return list(item[1])


def _store_addresses(host, addresses, now):
    _address_cache[host] = (now + ADDRESS_CACHE_SECONDS, list(addresses))


def _drop_address_cache(host):
    _address_cache.pop(host, None)


def _resolve_ipv4(host, budget):
    """走公网解析。系统解析没有超时，卡住时登录线程不会回来。"""
    deadline = time.time() + budget
    for resolver in PUBLIC_DNS_RESOLVERS:
        found = _ask_resolver(resolver, host, deadline)
        if found:
            return found
    return []


def _ask_resolver(resolver, host, deadline):
    remaining = deadline - time.time()
    if remaining <= 0:
        return []
    try:
        return _query_one_resolver(resolver, host, min(DNS_QUERY_TIMEOUT, remaining))
    except (OSError, ValueError, struct.error) as exc:
        logger.warning("解析微信地址失败 resolver=%s err=%s", resolver, type(exc).__name__)
        return []


def _query_one_resolver(resolver, host, timeout):
    query_id = random.randrange(0, DNS_ID_SPACE)
    packet = _recv_dns(resolver, _dns_query(host, query_id), timeout)
    return _a_records(packet, query_id)


def _recv_dns(resolver, query, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(query, (resolver, DNS_PORT))
        packet, _addr = sock.recvfrom(DNS_PACKET_LIMIT)
        return packet
    finally:
        sock.close()


def _dns_query(host, query_id):
    header = struct.pack(
        '!HHHHHH',
        query_id,
        DNS_FLAG_RECURSION,
        DNS_QUESTION_COUNT,
        DNS_NO_RECORD,
        DNS_NO_RECORD,
        DNS_NO_RECORD,
    )
    question = _encode_qname(host) + struct.pack('!HH', DNS_TYPE_A, DNS_CLASS_IN)
    return header + question


def _encode_qname(host):
    parts = []
    for label in host.strip('.').split('.'):
        encoded = label.encode('ascii')
        if not encoded or len(encoded) > DNS_LABEL_MAX:
            raise ValueError('dns label')
        parts.append(bytes((len(encoded),)) + encoded)
    return b''.join(parts) + b'\x00'


def _a_records(packet, query_id):
    if len(packet) < DNS_HEADER_LEN:
        raise ValueError('dns short')
    received_id, flags, questions, answers, _ns, _ar = struct.unpack(
        '!HHHHHH', packet[:DNS_HEADER_LEN])
    if received_id != query_id or not flags & DNS_FLAG_RESPONSE:
        return []
    if flags & DNS_FLAG_TRUNCATED or flags & DNS_RCODE_MASK:
        return []
    offset = _skip_questions(packet, DNS_HEADER_LEN, questions)
    return _collect_a(packet, offset, answers)


def _skip_questions(packet, offset, count):
    for _index in range(count):
        offset = _skip_name(packet, offset)
        offset += DNS_QUESTION_TAIL
        if offset > len(packet):
            raise ValueError('dns question')
    return offset


def _collect_a(packet, offset, count):
    found = []
    for _index in range(count):
        offset = _skip_name(packet, offset)
        if offset + DNS_ANSWER_META_LEN > len(packet):
            raise ValueError('dns answer')
        rtype, rclass, _ttl, rdlength = struct.unpack(
            '!HHIH', packet[offset:offset + DNS_ANSWER_META_LEN])
        offset += DNS_ANSWER_META_LEN
        if offset + rdlength > len(packet):
            raise ValueError('dns rdata')
        data = packet[offset:offset + rdlength]
        offset += rdlength
        if rtype == DNS_TYPE_A and rclass == DNS_CLASS_IN and len(data) == IPV4_OCTETS:
            found.append(socket.inet_ntoa(data))
    return found


def _skip_name(packet, offset):
    hops = 0
    while offset < len(packet) and hops <= DNS_NAME_HOPS:
        length = packet[offset]
        if length == 0:
            return offset + 1
        if length & DNS_POINTER_MASK == DNS_POINTER_MASK:
            if offset + 1 >= len(packet):
                break
            return offset + 2
        if length & DNS_POINTER_MASK:
            break
        offset += 1 + length
        hops += 1
    raise ValueError('dns name')


class _AddressPinnedHTTPSConnection(http.client.HTTPSConnection):
    """连指定地址，证书校验仍用域名。"""

    def __init__(self, hostname, ip, timeout):
        super().__init__(hostname, HTTPS_PORT, timeout=timeout)
        self._ip = ip

    def connect(self):
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        sock.settimeout(self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
        self.sock.settimeout(self.timeout)


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
