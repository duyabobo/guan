# -*- coding: utf-8 -*-
# __author__ = ‘du‘
# __created_at__ = '2018/12/2'
import hashlib
import secrets

_TEXT_HASH_ENCODING = 'utf-8'


def md5_hex(text):
    """Python 3 兼容：hashlib 需要 bytes 输入。"""
    if text is None:
        text = ''
    if isinstance(text, bytes):
        payload = text
    else:
        payload = str(text).encode(_TEXT_HASH_ENCODING)
    return hashlib.md5(payload).hexdigest()


_TOKEN_BYTES = 32


def generate_access_token(_login_user_id):
    """随机令牌。不包含用户编号，也不能由时间推算。"""
    return secrets.token_urlsafe(_TOKEN_BYTES)


def generate_secret(_access_token):
    """每次登录单独的签名密钥，不能由令牌推算出来。"""
    return secrets.token_urlsafe(_TOKEN_BYTES)
