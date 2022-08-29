#!/usr/bin/python
# -*- coding=utf-8 -*-
import functools
import time

from tornado import gen

from log import monitor_logger
from util.auth import Checker
from util.const.response import RESP_TOP_MONITOR_ERROR, RESP_SIGN_INVALID, RESP_OK
from util.obj_util import object_2_dict


class Response(object):
    def __init__(self, data=None, msg=RESP_OK):
        self.data = data
        self.msg = msg


def httpReturn(handler, response, err=None):
    logMsg = 'passportId: %s, method: %s, uri: %s, body: %s, accessToken: %s,' \
             ' respMsg: %s, respData: %s, tc: %s, error: %s' % \
             (handler.currentPassportId, handler.request.method, str(handler.request.uri), str(handler.request.body),
              handler.accessToken, response.msg, object_2_dict(response.data), time.time()-handler.timestamp, err)
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
