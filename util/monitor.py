#!/usr/bin/python
# -*- coding=utf-8 -*-
import time

from log import monitor_logger
from util.const import RESP_TOP_MONITOR_ERROR

monitorLogger = monitor_logger('super_monitor')


def super_monitor(method):
    def wrapper(self, *args, **kwargs):
        try:
            start = time.time()
            result = method(self, *args, **kwargs)
            end = time.time()
            # 正常日志
            monitorLogger.info(
                'method: %s, uri: %s, body: %s, access_token: %s, result: %s, request_time: %s' %
                (self.request.method, str(self.request.uri), str(self.request.body),
                 self.access_token, result, (end - start))
            )
        except Exception as e:
            # 出错日志
            resp = RESP_TOP_MONITOR_ERROR
            monitorLogger.exception(
                'method: %s, uri: %s, body: %s, access_token: %s, result: %s, error: %s' %
                (self.request.method, str(self.request.uri), str(self.request.body),
                 self.access_token, resp, e)
            )
            self.response(resp_normal=resp)
    return wrapper
