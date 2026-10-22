#! /usr/bin/env python
# -*- coding: utf-8 -*-


def session_payload(passport_id, sign_secret):
    """会话里只有通行证和签名密钥，不放 unionid 或其他身份密钥。"""
    return {
        "secret": sign_secret,
        "id": passport_id,
    }
