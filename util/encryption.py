#! /usr/bin/env python
# -*- coding: utf-8 -*-
import base64

import pyDes


def __encrypt(data, key):
    des = pyDes.des(key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    ecryptdata = des.encrypt(data)
    return bytes.decode(base64.b64encode(ecryptdata))  # base64 encoding bytes


def __decrypt(encryptedData, key):
    des = pyDes.des(key, pyDes.CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    data = des.decrypt(base64.b64decode(encryptedData))  # base64 decoding bytes
    return bytes.decode(data)


def getEncryptMail(openid, Mail):
    """返回加密后的邮箱字符串"""
    return __encrypt(Mail, openid[:8])


def getDecryptMail(openid, encryptedMail):
    """返回解密后的邮箱"""
    return __decrypt(encryptedMail, openid[:8])
