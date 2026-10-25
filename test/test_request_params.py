#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock

import pytest
from tornado.httputil import HTTPHeaders, HTTPServerRequest
from tornado.web import Application

from handler.basehandler import BaseHandler
from util.errors import InvalidParameter


def _handler(uri='/x', body=b'', content_type=None):
    headers = HTTPHeaders()
    if content_type:
        headers['Content-Type'] = content_type
    request = HTTPServerRequest(
        method='GET', uri=uri, headers=headers, body=body, connection=MagicMock(),
    )
    return BaseHandler(Application(), request)


def test_int_parameter_reads_query():
    assert _handler('/x?guanId=7').getIntParameter('guanId', minimum=1) == 7


def test_int_parameter_reads_json_body_with_charset_content_type():
    handler = _handler(body=json.dumps({'guanId': 9}).encode(), content_type='application/json; charset=utf-8')
    assert handler.getIntParameter('guanId', minimum=1) == 9


def test_int_parameter_missing_is_rejected():
    with pytest.raises(InvalidParameter):
        _handler('/x').getIntParameter('guanId')


def test_int_parameter_default_when_missing():
    assert _handler('/x').getIntParameter('limit', default=20, minimum=1, maximum=50) == 20


@pytest.mark.parametrize('uri', ['/x?limit=abc', '/x?limit=0', '/x?limit=51', '/x?limit=-3'])
def test_int_parameter_rejects_bad_or_out_of_range(uri):
    with pytest.raises(InvalidParameter):
        _handler(uri).getIntParameter('limit', default=20, minimum=1, maximum=50)


def test_int_parameter_choices():
    assert _handler('/x?opType=2').getIntParameter('opType', choices=(1, 2, 3)) == 2
    with pytest.raises(InvalidParameter):
        _handler('/x?opType=9').getIntParameter('opType', choices=(1, 2, 3))


@pytest.mark.parametrize('value', ['nan', 'inf', '-inf', 'abc', '181'])
def test_float_parameter_rejects_non_finite_and_out_of_range(value):
    with pytest.raises(InvalidParameter):
        _handler('/x?longitude=%s' % value).getFloatParameter('longitude', default=-1, minimum=-180.0, maximum=180.0)


def test_float_parameter_default_and_value():
    handler = _handler('/x?longitude=116.4')
    assert handler.getFloatParameter('longitude', default=-1, minimum=-180.0, maximum=180.0) == 116.4
    assert _handler('/x').getFloatParameter('longitude', default=-1) == -1


def test_request_parameter_falls_back_to_default_instead_of_raising():
    assert _handler('/x?n=abc').getRequestParameter('n', default=5, paraType=int) == 5
    assert _handler('/x').getRequestParameter('n', default='') == ''


def test_non_object_json_body_is_treated_as_empty():
    handler = _handler(body=b'[1, 2]', content_type='application/json')
    assert handler.getRequestParameter('a', default='d') == 'd'


def test_broken_json_body_does_not_raise():
    handler = _handler(body=b'{oops', content_type='application/json')
    assert handler.getRequestParameter('a', default='d') == 'd'
