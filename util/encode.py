# -*- coding: utf-8 -*-
# __author__ = ‘du‘
# __created_at__ = '2018/12/2'
import hashlib
import json
import time
from random import randint

import jwt

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


def general_code():
    """
    生成随机验证码
    :return:
    """
    return ''.join(map(lambda x: str(randint(0, 9)), range(6)))


def jwt_encode(payload, key):
    """
    可解密的 jwt 加密
    :param payload:
    :param key:
    :return:
    """
    return jwt.encode(payload, key, algorithm='HS256')


def jwt_decode(jwt_str, key):
    """
    jwt 解密
    :param jwt_str:
    :param key:
    :return:
    """
    try:
        decoded = jwt.decode(jwt_str, key, algorithms=['HS256'])
    except Exception:
        return {}
    if isinstance(decoded, dict):
        return decoded
    if decoded:
        try:
            return json.loads(decoded)
        except Exception:
            pass
    return {}


def generate_access_token(login_user_id):
    """
    md5 生成 accessToken
    :param login_user_id:
    :return:
    """
    timestamp = str(time.time())
    return md5_hex(timestamp + str(login_user_id))


def generate_secret(accessToken):
    """"""
    timestamp = str(time.time())
    return md5_hex(timestamp + str(accessToken))


def generate_encrypted_password(password):
    """
    md5 生成加密密码
    :param password:
    :return:
    """
    return md5_hex(password) if password else None
