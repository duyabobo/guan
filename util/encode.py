# -*- coding: utf-8 -*-
# __author__ = ‘du‘
# __created_at__ = '2018/12/2'
import hashlib
import time

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
