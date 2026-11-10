#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket
import struct
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import util.wx_mini as wx_mini

_QUERY_ID = 0x1234
_SAMPLE_IP = '1.2.3.4'
_OTHER_IP = '5.6.7.8'
_ANSWER_TTL = 60
_RESOLVE_BUDGET = 5
_CLOCK_START = 1000.0
_POINTER_SHIFT = 8
_RCODE_REFUSED = 5
_FLAGS_OK = wx_mini.DNS_FLAG_RESPONSE | wx_mini.DNS_FLAG_RECURSION
_FLAGS_TRUNCATED = wx_mini.DNS_FLAG_RESPONSE | wx_mini.DNS_FLAG_TRUNCATED
_FLAGS_REFUSED = wx_mini.DNS_FLAG_RESPONSE | _RCODE_REFUSED


@pytest.fixture(autouse=True)
def _clear_address_cache():
    wx_mini._address_cache.clear()
    wx_mini._preferred_address.clear()
    yield
    wx_mini._address_cache.clear()
    wx_mini._preferred_address.clear()


def _name_pointer(offset):
    return (wx_mini.DNS_POINTER_MASK << _POINTER_SHIFT) | offset


def _answer(ip):
    return struct.pack(
        '!HHHIH',
        _name_pointer(wx_mini.DNS_HEADER_LEN),
        wx_mini.DNS_TYPE_A,
        wx_mini.DNS_CLASS_IN,
        _ANSWER_TTL,
        wx_mini.IPV4_OCTETS,
    ) + socket.inet_aton(ip)


def _packet(query_id, flags, answers):
    question = wx_mini._encode_qname(wx_mini.WX_API_HOST) + struct.pack(
        '!HH', wx_mini.DNS_TYPE_A, wx_mini.DNS_CLASS_IN)
    header = struct.pack(
        '!HHHHHH',
        query_id,
        flags,
        wx_mini.DNS_QUESTION_COUNT,
        len(answers),
        wx_mini.DNS_NO_RECORD,
        wx_mini.DNS_NO_RECORD,
    )
    return header + question + b''.join(answers)


def test_parse_a_record():
    packet = _packet(_QUERY_ID, _FLAGS_OK, [_answer(_SAMPLE_IP), _answer(_OTHER_IP)])
    assert wx_mini._a_records(packet, _QUERY_ID) == [_SAMPLE_IP, _OTHER_IP]


def test_parse_rejects_bad_packet():
    ok = _packet(_QUERY_ID, _FLAGS_OK, [_answer(_SAMPLE_IP)])
    assert wx_mini._a_records(ok, _QUERY_ID + 1) == []
    assert wx_mini._a_records(_packet(_QUERY_ID, _FLAGS_TRUNCATED, [_answer(_SAMPLE_IP)]), _QUERY_ID) == []
    assert wx_mini._a_records(_packet(_QUERY_ID, _FLAGS_REFUSED, [_answer(_SAMPLE_IP)]), _QUERY_ID) == []
    with pytest.raises(ValueError):
        wx_mini._a_records(b'short', _QUERY_ID)
    with pytest.raises(ValueError):
        wx_mini._encode_qname('bad..com')


def test_second_address_is_used_when_first_times_out(monkeypatch):
    calls = []
    both_started = threading.Barrier(2)

    def request_one(ip, path, timeout):
        calls.append(ip)
        both_started.wait(1)
        if ip == '1.1.1.1':
            raise socket.timeout()
        return b'{"openid":"o"}'

    monkeypatch.setattr(wx_mini, '_addresses_for', lambda host, deadline: ['1.1.1.1', '2.2.2.2'])
    monkeypatch.setattr(wx_mini, '_request_one', request_one)
    assert wx_mini._fetch_session('/sns/jscode2session', wx_mini.CODE_TO_SESSION_TIMEOUT) == b'{"openid":"o"}'
    assert set(calls) == {'1.1.1.1', '2.2.2.2'}


def test_fetch_without_address(monkeypatch):
    monkeypatch.setattr(wx_mini, '_addresses_for', lambda host, deadline: [])
    with pytest.raises(socket.gaierror):
        wx_mini._fetch_session('/sns/jscode2session', _RESOLVE_BUDGET)


def test_slow_address_does_not_hold_login(monkeypatch):
    release = threading.Event()

    def request_one(ip, path, timeout):
        if ip != '3.3.3.3':
            release.wait(2)
            raise socket.timeout()
        return b'{"openid":"o"}'

    monkeypatch.setattr(
        wx_mini, '_addresses_for',
        lambda host, deadline: ['1.1.1.1', '2.2.2.2', '3.3.3.3'])
    monkeypatch.setattr(wx_mini, '_request_one', request_one)
    started = time.time()
    try:
        assert wx_mini._fetch_session('/sns/jscode2session', 5) == b'{"openid":"o"}'
        assert time.time() - started < 0.5
    finally:
        release.set()
    assert wx_mini._preferred_address[wx_mini.WX_API_HOST] == '3.3.3.3'


def test_race_stops_at_address_cap(monkeypatch):
    calls = []
    seen = threading.Event()

    def request_one(ip, path, timeout):
        calls.append(ip)
        if len(calls) >= wx_mini.MAX_RACE_ADDRESSES:
            seen.set()
        raise socket.timeout()

    monkeypatch.setattr(
        wx_mini, '_addresses_for',
        lambda host, deadline: ['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4', '5.5.5.5'])
    monkeypatch.setattr(wx_mini, '_request_one', request_one)
    with pytest.raises(socket.timeout):
        wx_mini._fetch_session('/sns/jscode2session', 5)
    assert seen.wait(1)
    assert set(calls) == {'1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4'}


def test_working_address_is_remembered(monkeypatch):
    def request_one(ip, path, timeout):
        if ip == '2.2.2.2':
            return b'{}'
        raise socket.timeout()

    monkeypatch.setattr(wx_mini, '_addresses_for', lambda host, deadline: ['1.1.1.1', '2.2.2.2'])
    monkeypatch.setattr(wx_mini, '_request_one', request_one)
    assert wx_mini._fetch_session('/sns/jscode2session', 5) == b'{}'
    assert wx_mini._preferred_address[wx_mini.WX_API_HOST] == '2.2.2.2'


def test_blackhole_connect_returns_within_timeout():
    outcome = {}

    def run():
        try:
            wx_mini._connect_ip('192.0.2.1', 0.2)
        except OSError as exc:
            outcome['error'] = exc

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(1)
    assert not thread.is_alive()
    assert outcome.get('error') is not None


def test_failed_fetch_drops_cached_address(monkeypatch):
    wx_mini._store_addresses(wx_mini.WX_API_HOST, ['9.9.9.9'], time.time())

    def request_one(ip, path, timeout):
        raise socket.timeout()

    monkeypatch.setattr(wx_mini, '_request_one', request_one)
    with pytest.raises(socket.timeout):
        wx_mini._fetch_session('/sns/jscode2session', _RESOLVE_BUDGET)
    assert wx_mini.WX_API_HOST not in wx_mini._address_cache


def test_first_resolver_stops_the_rest(monkeypatch):
    seen = []

    def query(resolver, host, timeout):
        seen.append(resolver)
        return ['9.9.9.9']

    monkeypatch.setattr(wx_mini, '_query_one_resolver', query)
    assert wx_mini._resolve_ipv4(wx_mini.WX_API_HOST, _RESOLVE_BUDGET) == ['9.9.9.9']
    assert seen == [wx_mini.PUBLIC_DNS_RESOLVERS[0]]


def test_public_dns_uses_next_resolver_when_first_is_empty(monkeypatch):
    seen = []

    def query(resolver, host, timeout):
        seen.append(resolver)
        if resolver == wx_mini.PUBLIC_DNS_RESOLVERS[0]:
            return []
        return ['9.9.9.9']

    monkeypatch.setattr(wx_mini, '_query_one_resolver', query)
    assert wx_mini._resolve_ipv4(wx_mini.WX_API_HOST, _RESOLVE_BUDGET) == ['9.9.9.9']
    assert seen == list(wx_mini.PUBLIC_DNS_RESOLVERS)


def test_resolve_returns_empty_when_every_resolver_is_empty(monkeypatch):
    monkeypatch.setattr(wx_mini, '_query_one_resolver', lambda resolver, host, timeout: [])
    assert wx_mini._resolve_ipv4(wx_mini.WX_API_HOST, _RESOLVE_BUDGET) == []


def test_address_cache_hits_then_expires(monkeypatch):
    calls = []

    def resolve(host, budget):
        calls.append(host)
        return ['8.8.8.8']

    monkeypatch.setattr(wx_mini, '_resolve_ipv4', resolve)
    deadline = time.time() + _RESOLVE_BUDGET
    assert wx_mini._addresses_for(wx_mini.WX_API_HOST, deadline) == ['8.8.8.8']
    assert wx_mini._addresses_for(wx_mini.WX_API_HOST, deadline) == ['8.8.8.8']
    assert calls == [wx_mini.WX_API_HOST]
    wx_mini._address_cache[wx_mini.WX_API_HOST] = (
        time.time() - wx_mini.ADDRESS_CACHE_SECONDS, ['8.8.8.8'])
    assert wx_mini._addresses_for(wx_mini.WX_API_HOST, deadline) == ['8.8.8.8']
    assert calls == [wx_mini.WX_API_HOST, wx_mini.WX_API_HOST]
