#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""请求被拒绝的原因。用显式异常，不用 assert：python -O 会把 assert 整个去掉，校验就失效了。"""


class RequestRejected(Exception):
    """请求在校验阶段被拒绝。"""


class SignatureInvalid(RequestRejected):
    """请求签名对不上。"""


class ReplayDetected(RequestRejected):
    """同一个请求序号在有效期内重复出现。"""


class RateLimitExceeded(RequestRejected):
    """同一 IP 或同一令牌在窗口内请求过于频繁。"""


class RuntimeIdentityMissing(RequestRejected):
    """Redis 里找不到这个人的运行时身份密钥，需要重新登录。"""


class InvalidParameter(Exception):
    """入参缺失、类型不对或越界。属于调用方错误，不是服务器错误，也不计入签名失败。"""
