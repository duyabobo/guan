#!/usr/bin/python
# -*- coding=utf-8 -*-
import time
import hashlib

from log import monitor_logger
from util.const import RESP_TOP_MONITOR_ERROR, RESP_SIGN_INVALID

monitorLogger = monitor_logger('superMonitor')


LOGIN_API = "/login"  # 白名单api，可以直接绕过签名校验


class SignChecker(object):
    def __init__(self, handler):
        self.request = handler.request
        self.token = handler.accessToken
        self.sign = handler.sign
        self.timestamp = handler.timestamp
        self.currentPassportId = handler.currentPassportId

    def checkSignWithoutToken(self):
        # 登录接口签名验证
        return hashlib.md5(self.timestamp).hexdigest().upper() == self.sign

    def checkSignWithToken(self, requestContent):
        if not self.currentPassportId:
            return False
        return hashlib.md5(requestContent).hexdigest().upper() == self.sign

    @property
    def signIsValid(self):
        """
        签名校验: 如果通过就返回true，如果不通过就返回false
        """
        # 必传参数校验
        if not self.sign:
            return False
        if not self.timestamp:
            return False

        if time.time() - self.timestamp > 10:  # 10s前的请求
            return False
        # 防重放 todo

        if self.request.path == LOGIN_API:  # 登录接口
            return self.checkSignWithoutToken()

        requestContent = '%s:%s' % (self.request.uri, self.request.body)
        return self.checkSignWithToken(requestContent)


def superMonitor(method):
    def wrapper(self, *args, **kwargs):
        # if not SignChecker(self).signIsValid:
        #     # 安全校验失败
        #     resp = RESP_SIGN_INVALID
        #     monitorLogger.error(
        #         'method: %s, uri: %s, body: %s, accessToken: %s, result: %s' %
        #         (self.request.method, str(self.request.uri), str(self.request.body),
        #          self.accessToken, resp)
        #     )
        #     self.response(respNormal=resp)
        #     return
        try:
            start = time.time()
            ret = method(self, *args, **kwargs)
            end = time.time()
            # 正常日志
            monitorLogger.info(
                'method: %s, uri: %s, body: %s, accessToken: %s, ret: %s, request_time: %s' %
                (self.request.method, str(self.request.uri), str(self.request.body),
                 self.accessToken, ret, (end - start))
            )
            return
        except Exception as e:
            # 出错日志
            resp = RESP_TOP_MONITOR_ERROR
            monitorLogger.exception(
                'method: %s, uri: %s, body: %s, accessToken: %s, result: %s, error: %s' %
                (self.request.method, str(self.request.uri), str(self.request.body),
                 self.accessToken, resp, e)
            )
            self.response(respNormal=resp)
            return
    return wrapper
