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
            return result
        except Exception as e:
            resp = self.response(resp_normal=RESP_TOP_MONITOR_ERROR)
            # 出错日志
            monitorLogger.exception(
                'method: %s, uri: %s, body: %s, access_token: %s, result: %s, error: %s' %
                (self.request.method, str(self.request.uri), str(self.request.body),
                 self.access_token, resp, e)
            )
    return wrapper


def super_monitor_chat(method):
    def wrapper(self, *args, **kwargs):
        try:
            start = time.time()
            result = method(self, *args, **kwargs)
            end = time.time()
            # 正常日志
            monitorLogger.info(
                'method: %s, uri: %s, args: %s, result: %s, request_time: %s' %
                (self.request.method, str(self.request.uri), str(args), result, (end - start))
            )
            return result
        except Exception as e:
            # 出错日志
            monitorLogger.exception(
                'method: %s, uri: %s, body: %s, error: %s' %
                (self.request.method, str(self.request.uri), str(self.request.body), e)
            )
    return wrapper
