#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 结合 redis 实现一人一密的接口安全认证方案。加密方案使用jwt，但是实际落地不仅限于 jwt（md5等均可），jwt 方便之处是可以自带并自检 exp。
# 可以防止撞库，撞对一个的概率是1/(52**32)。如果有撞库现象，可以对 ip 进行频次监控。
# 不怕密钥泄漏，密钥不会传输，不怕被抓取。如果用户主动伪造攻击，可以对 uid 进行频次监控。
# 不怕加密算法泄漏，因为一人一密。
# 可以防止重放攻击。
import base64
import json

import hashlib
import urlparse

from ral.passport import checkUnique, setFailCnt, setSuccessCnt, checkFailedCnt, checkSuccessCnt

ALGORITHM_SIGN = 'HS256'

# 下面是限流方案。滑动窗口算法实现，更精准，但也更复杂，姑且不考虑。如有意，可以加多个限流标准：比如现在建立的是分钟级别的，可以增加十分钟级别的，半小时级别的...。
# nginx ngx_http_limit_req_module 进行频率限制，也可以应用程序结合 redis 进行频率监控。
# 后者对嫌疑请求的处理更灵活（比如出滑块，返回假数据，返回错误提示等），前者对恶意 ip 或关键 url 进行保护（直接拒绝响应）。
# 一般应用程序内部滑块处理：
# 0，什么都不可信：不会有人知道这个接口？不会有人知道加密算法？不会有人无聊到压测这个接口？不会有人想获取这个接口到返回数据？no。所以，尽可能多的接口使用 sign 验证。
# 1，无 sign 接口，对 ip 进行频次监控并处理。
# 2，有 sign 接口，只需要 uid 进行频次监控并处理。
# 3，对关键接口保护，比如读写关键数据的接口，比如资源消耗严重的接口，在1，2的基础上，增加对于指定 url 的监控和处理。
# 4，一般 1/2 对触发频次阈值非常宽松，3 可以适当严格。
# 5, 滑块验证通过后，可以对请求放行，并对频次清零重新计数监控，做到对正常用户的最小影响。
# 6，尽可能实时的自动化的维护一个 ip 黑名单，以及一个 uid 黑名单，并在应用中对这些 ip/uid 发出的请求进行处理。
# 7，如果 6 中黑名单请求量特别大，已经影响到系统正常提供服务，就直接在 ng 进行 503 拒绝响应。


class Checker(object):
    def __init__(self, handler):
        self.remote_ip = handler.request.remote_ip
        self.path = handler.request.path
        self.method = handler.request.method
        self.query = handler.request.query
        self.body = handler.request.body
        self.requestSeq = handler.requestSeq
        self.currentPassport = handler.currentPassport
        self.accessToken = self.currentPassport.get('accessToken', '')
        self.sign = handler.sign
        self.secret = self.currentPassport.get('secret', '')

    def check(self):
        """对请求进行检查，拦截无效/非法/恶意的请求。
        攻击是不能完全防控的，还需要监控日志识别恶意ip和虚假user，并进行管控和清理。"""
        checkFailedCnt(self.remote_ip)  # 有爬取用户信息攻击行为时放开，1次redis查询操作
        checkSuccessCnt(self.accessToken)  # 有消耗服务资源攻击行为时放开，1～3次redis操作
        self.check_sign(self.secret)  # 1次解密操作
        checkUnique(self.accessToken, self.requestSeq)  # 1～2次redis写入操作

    def fail(self):
        """校验失败处理"""
        setFailCnt(self.remote_ip)

    def success(self):
        """校验成功处理"""
        setSuccessCnt(self.accessToken)

    def getContentFromQuery(self, data, sep):
        if type(data) == str:
            return base64.b64encode(data)
        if type(data) == unicode:
            return base64.b64encode(data.encode('utf8'))
        if type(data) == int:
            return base64.b64encode(str(data))
        if type(data) == float:
            return base64.b64encode(str(data))
        if type(data) == dict:
            sortedItems = sorted(data.items(), key=lambda x: x[0])
            contentList = [self.getContentFromQuery(k, sep) + sep + self.getContentFromQuery(v, sep) for k, v in sortedItems]
            return sep.join(contentList)
        if type(data) == list:
            contentList = [self.getContentFromQuery(i, sep) + sep + self.getContentFromQuery(data[i], sep) for i in range(len(data))]
            return sep.join(contentList)
        return ""

    def check_sign(self, secret):
        """签名认证"""
        # 处理参数
        requestParams = {
            'secret': secret,
            'path': self.path,
            'method': self.method,
        }
        if self.body:
            requestParams.update(json.loads(self.body))
        if self.query:
            queryParams = {k: v for k, v in urlparse.parse_qsl(self.query, keep_blank_values=1)}
            requestParams.update(queryParams)
        # 加密校验
        content = self.getContentFromQuery(requestParams, "|")
        assert self.sign == hashlib.md5(content).hexdigest(), '签名验证失败'
