#!/usr/bin/python
# -*- coding=utf-8 -*-
import functools
import time

from tornado import gen

import util.ctx
from util.log import monitor_logger
from util.auth import Checker
from util.const.response import RESP_TOP_MONITOR_ERROR, RESP_SIGN_INVALID, RESP_OK
from util.log_redact import redact_body, redact_uri, summarize_for_log
from util.obj_util import object_2_dict


class Response(object):
    def __init__(self, data=None, msg=RESP_OK):
        self.data = data
        self.msg = msg


def _body_for_log(handler):
    content_type = handler.request.headers.get('Content-Type', '') or ''
    if 'multipart/form-data' in content_type:
        return 'multipart'
    body = handler.request.body_arguments or handler.request.body
    return redact_body(body)


def _resp_for_log(_path, data):
    return summarize_for_log(object_2_dict(data))


def httpReturn(handler, response, err=None):
    manager = util.ctx.getManager()
    manager.tc_child_out()
    logMsg = 'passportId: %s, method: %s, uri: %s, body: %s, accessTokenLen: %s,' \
             ' respMsg: %s, respData: %s, tc: %s, error: %s, tc_tree=%s' % \
             (handler.currentPassportId, handler.request.method, redact_uri(str(handler.request.uri)),
              _body_for_log(handler), len(handler.accessToken or ''),
              response.msg, _resp_for_log(handler.request.path, response.data),
              time.time()-handler.timestamp, err, manager.timecost_tree)
    if err is None:
        monitor_logger.info(logMsg)
    else:
        monitor_logger.exception(logMsg)
    return handler.response(response)


def superMonitor(func):
    @functools.wraps(func)
    def wrapper(handler, *args, **kwargs):
        # 处理前校验
        checker = Checker(handler)
        try:
            checker.check()
        except Exception as e:  # 校验失败
            checker.fail()
            httpReturn(handler, Response(msg=RESP_SIGN_INVALID), err=e)
            return
        else:  # 校验成功
            checker.success()
        # 开始处理请求
        try:
            response = func(handler, *args, **kwargs)
        except Exception as e:  # 处理失败
            httpReturn(handler, Response(msg=RESP_TOP_MONITOR_ERROR), err=e)
            return
        else:  # 处理成功
            httpReturn(handler, response)
            return
    return wrapper


def superGenMonitor(func):
    # 要放到@gen.coroutine上面装饰
    @functools.wraps(func)
    @gen.coroutine
    def wrapper(handler, *args, **kwargs):
        # 处理前校验
        checker = Checker(handler)
        try:
            checker.check()
        except Exception as e:  # 校验失败
            checker.fail()
            httpReturn(handler, Response(msg=RESP_SIGN_INVALID), err=e)
            return
        else:  # 校验成功
            checker.success()
        # 开始处理请求
        try:
            response = yield func(handler, *args, **kwargs)
        except Exception as e:  # 处理失败
            httpReturn(handler, Response(msg=RESP_TOP_MONITOR_ERROR), err=e)
            return
        else:  # 处理成功
            httpReturn(handler, response)
            return
    return wrapper
