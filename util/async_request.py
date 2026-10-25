#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from urllib import parse as urlparse

import tornado
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest

from util.const.mini_program import WX_API_HOST
from util.log import monitor_logger


def _log_url(url):
    if url and WX_API_HOST in url:
        return url.split('?', 1)[0]
    return url


def _joined_urls(requests):
    return '|'.join(_log_url(item[0].url) for item in requests.values())


@gen.coroutine
def asyncRequest(url, data_json, method='GET', timeout=1, need_retry=False, quiet=False):
    """
    对Tornado AsyncHttpClient的封装。支持重试。
    """
    # warning：如果调用不是幂等的，不要重试。这个有调用方控制。
    # warning: 如果是请求超时，不会重试。这个是实现方控制。
    if method == 'GET' and data_json:
        if '?' not in url:
            url = '{}?{}'.format(url, urlparse.urlencode(data_json))
        else:
            url = '{}&{}'.format(url, urlparse.urlencode(data_json))
        body = None
    else:
        body = json.dumps(data_json)
    logged_url = _log_url(url)
    logged_body = '' if quiet else body
    http_client = AsyncHTTPClient()

    retry_cnt = 3 if need_retry else 1
    last_error = None
    for r in range(retry_cnt):
        try:
            headers = {'Content-Type': 'application/json'}
            monitor_logger.info('异步调用http接口 触发 url=%s body=%s headers=%s'
                                'active_num=%s wait_num=%s queue_len=%s actives=%s waits=%s',
                                logged_url, logged_body, headers,
                                len(http_client.active), len(http_client.waiting), len(http_client.queue),
                                _joined_urls(http_client.active),
                                _joined_urls(http_client.waiting))
            req = HTTPRequest(url, method=method, body=body, validate_cert=True,
                              request_timeout=timeout, headers=headers, allow_nonstandard_methods=True)
            res = yield http_client.fetch(req)
            resp = json.loads(res.body)
            logged_resp = 'omitted' if quiet else resp
            logged_detail = '' if quiet else str(res.__dict__)
            monitor_logger.info('异步调用http接口 成功 method=%s url=%s body=%s res.code=%s resp=%s rps_detail=%s',
                                method, logged_url, logged_body, res.code, logged_resp, logged_detail)
            raise gen.Return(resp)
        except tornado.gen.Return:
            raise
        except Exception as exc:
            last_error = exc
            logged_exc = type(exc).__name__ if quiet else str(exc.__dict__)
            monitor_logger.exception('异步调用http接口 异常 method=%s url=%s body=%s type_e=%s exc=%s',
                                    method, logged_url, logged_body, type(exc), logged_exc)

        if r == retry_cnt - 1:
            monitor_logger.error('异步调用http接口 重试结束调用失败 retry_cnt=%s r=%s', retry_cnt, r)
            raise last_error
