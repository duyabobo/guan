#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 一人一密的请求签名：用会话里的 secret 对 path、method 和参数做 md5，并校验序号防重放。
from ral.passport import checkUnique, setFailCnt, setSuccessCnt, checkFailedCnt, checkSuccessCnt
from service.identity.runtime_key import has_unionid, touch_unionid
from util.const.identity import LOGIN_PATH
from util.sign_content import sign_digest


class Checker(object):
    def __init__(self, handler):
        self.remote_ip = handler.request.remote_ip
        self.path = handler.request.path
        self.method = handler.request.method
        self.query = handler.request.query
        self.body = handler.request.body
        self.content_type = handler.request.headers.get('Content-Type', '') or ''
        self.form_arguments = handler.request.arguments
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
        if self.path == LOGIN_PATH:
            return
        self.check_sign(self.secret)  # 1次解密操作
        self.require_runtime_key()
        checkUnique(self.accessToken, self.requestSeq)  # 1～2次redis写入操作

    def fail(self):
        """校验失败处理"""
        setFailCnt(self.remote_ip)

    def success(self):
        """校验成功处理"""
        setSuccessCnt(self.accessToken)

    def require_runtime_key(self):
        """已登录请求必须能在 Redis 里找到这次微信登录留下的 unionid。"""
        if self.path == LOGIN_PATH:
            return
        passport_id = int(self.currentPassport.get('id') or 0)
        if not passport_id:
            return
        assert has_unionid(passport_id), 'runtime identity missing'
        touch_unionid(passport_id)

    def check_sign(self, secret):
        digest = sign_digest(
            self.path, self.method, secret, self.body, self.query,
            self.content_type, self.form_arguments,
        )
        assert self.sign == digest, "签名验证失败"
