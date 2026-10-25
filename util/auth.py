#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 一人一密的请求签名：用会话里的 secret 对 path、method 和参数做 md5，并校验序号防重放。
import hmac

from ral.passport import checkUnique, setFailCnt, setSuccessCnt, checkFailedCnt, checkSuccessCnt
from service.identity.runtime_key import has_unionid, touch_unionid
from util.const.identity import LOGIN_PATH
from util.errors import RuntimeIdentityMissing, SignatureInvalid
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
        self.accessToken = handler.accessToken
        # 会话里没有 accessToken 字段，必须取请求带来的令牌；没登录的请求按 IP 计数，不能所有人共用一个计数
        self.rate_subject = self.accessToken or 'ip:%s' % self.remote_ip
        self.sign = handler.sign
        self.secret = self.currentPassport.get('secret', '')

    def check(self):
        """对请求进行检查，拦截无效/非法/恶意的请求。校验不过抛 RequestRejected 的子类。
        攻击是不能完全防控的，还需要监控日志识别恶意ip和虚假user，并进行管控和清理。"""
        checkFailedCnt(self.remote_ip)  # 有爬取用户信息攻击行为时放开，1次redis查询操作
        checkSuccessCnt(self.rate_subject)  # 有消耗服务资源攻击行为时放开，1～3次redis操作
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
        setSuccessCnt(self.rate_subject)

    def require_runtime_key(self):
        """已登录请求必须能在 Redis 里找到这次微信登录留下的 unionid。"""
        passport_id = int(self.currentPassport.get('id') or 0)
        if not passport_id:
            return
        if not has_unionid(passport_id):
            raise RuntimeIdentityMissing('runtime identity missing passport=%s' % passport_id)
        touch_unionid(passport_id)

    def check_sign(self, secret):
        digest = sign_digest(
            self.path, self.method, secret, self.body, self.query,
            self.content_type, self.form_arguments,
        )
        # 常数时间比较，避免按字节计时猜签名
        if not self.sign or not hmac.compare_digest(self.sign.encode('utf-8'), digest.encode('utf-8')):
            raise SignatureInvalid('签名验证失败')
