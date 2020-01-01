# -*- coding: utf-8 -*-
# __author__ = ‘du‘
# __created_at__ = '2018/12/2'
import hashlib
import json
import time
from random import randint

import jwt


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
    return jwt.encode(payload, key)


def jwt_decode(jwt_str, key):
    """
    jwt 解密
    :param jwt_str:
    :param key:
    :return:
    """
    jwt_json_str = jwt.decode(jwt_str, key)
    jwt_json = {}
    if jwt_json_str:
        try:
            jwt_json = json.loads(jwt_json_str)
        except Exception:
            pass
    return jwt_json


def generate_access_token(login_user_id):
    """
    md5 生成 access_token
    :param login_user_id:
    :return:
    """
    timestamp = str(time.time())
    return hashlib.md5(timestamp+str(login_user_id)).hexdigest()


def generate_encrypted_password(password):
    """
    md5 生成加密密码
    :param password:
    :return:
    """
    return hashlib.md5(password).hexdigest() if password else None
