#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib

import tornado
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest

from log import monitor_logger

monitorLogger = monitor_logger('superMonitor')


@gen.coroutine
def asyncRequest(url, data_json, method='GET', timeout=1, need_retry=False):
    """
    对Tornado AsyncHttpClient的封装。支持重试。
    @param url:
    @param data_json:
    @param method:
    @param timeout:
    @param need_retry: 是否需要重试，如果是，还会自动重试2次。
    @return:
    """
    # warning：如果调用不是幂等的，不要重试。这个有调用方控制。
    # warning: 如果是请求超时，不会重试。这个是实现方控制。
    if method == 'GET' and data_json:
        url = '{}?{}'.format(url, urllib.urlencode(data_json))
        body = None
    else:
        body = json.dumps(data_json)
    http_client = AsyncHTTPClient()

    retry_cnt = 3 if need_retry else 1
    for r in range(retry_cnt):
        try:
            headers = {'Content-Type': 'application/json'}
            monitorLogger.info('异步调用http接口 触发 url=%s body=%s headers=%s'
                               'active_num=%s wait_num=%s queue_len=%s actives=%s waits=%s',
                               url, body, headers,
                               len(http_client.active), len(http_client.waiting), len(http_client.queue),
                               '|'.join([_[0].url for _ in http_client.active.values()]),
                               '|'.join([_[0].url for _ in http_client.waiting.values()]))
            req = HTTPRequest(url, method=method, body=body, validate_cert=False,
                              request_timeout=timeout, headers=headers, allow_nonstandard_methods=True)
            res = yield http_client.fetch(req)
            resp = json.loads(res.body)
            monitorLogger.info('异步调用http接口 成功 method=%s url=%s body=%s res.code=%s resp=%s rps_detail=%s',
                               method, url, body, res.code, resp, str(res.__dict__))
            raise gen.Return(resp)
        except tornado.gen.Return as e:
            raise e
        except Exception as e:
            monitorLogger.exception('异步调用http接口 异常 method=%s url=%s body=%s type_e=%s exc=%s',
                                    method, url, body, type(e), str(e.__dict__))

        if r == retry_cnt - 1:
            monitorLogger.error('异步调用http接口 重试结束调用失败 retry_cnt=%s r=%s', retry_cnt, r)
            raise gen.Return()
