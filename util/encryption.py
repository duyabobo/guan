#! /usr/bin/env python
# -*- coding: utf-8 -*-
import base64

import pyDes

_TEXT_ENCODING = 'utf-8'


def _to_bytes(text):
    if isinstance(text, bytes):
        return text
    return str(text).encode(_TEXT_ENCODING)


def __encrypt(data, key):
    des = pyDes.des(key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    ecryptdata = des.encrypt(_to_bytes(data))
    return base64.b64encode(ecryptdata).decode('ascii')


def __decrypt(encryptedData, key):
    des = pyDes.des(key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    data = des.decrypt(base64.b64decode(_to_bytes(encryptedData)))
    return data.decode(_TEXT_ENCODING)


def getEncryptMail(openid, Mail):
    """返回加密后的邮箱字符串"""
    return __encrypt(Mail, openid[:8])


def getDecryptMail(openid, encryptedMail):
    """返回解密后的邮箱"""
    return __decrypt(encryptedMail, openid[:8])
