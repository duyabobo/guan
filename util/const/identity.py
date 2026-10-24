#! /usr/bin/env python
# -*- coding: utf-8 -*-

PROVIDER_WECHAT = 'wechat'
PROVIDER_NATIONAL_NETWORK = 'national_network'

# 当前用来加密敏感信息的身份提供方。换提供方后，旧密文仍按记录上的 key_provider 解密。
ACTIVE_KEY_PROVIDER = PROVIDER_WECHAT

KIND_VOICE = 'voice'
KIND_PHONE = 'phone'
KIND_MAIL = 'mail'
KIND_PHOTO = 'photo'
SENSITIVE_KINDS = (KIND_VOICE, KIND_PHONE, KIND_MAIL, KIND_PHOTO)

AES_KEY_BYTES = 32
AES_NONCE_BYTES = 12
AES_TAG_BYTES = 16
HKDF_INFO = b'guan-sensitive-v1'
HKDF_SALT = b'guan-sensitive-salt-v1'

PURPOSE_ENCRYPT_STORE = 'encrypt_store'
PURPOSE_SUBSCRIBE_SEND = 'subscribe_send'
PURPOSE_PHONE_NOTIFY = 'phone_notify'
PURPOSE_MIN_LENGTH = 4

MAX_VOICE_BYTES = 5 * 1024 * 1024
VOICE_CONTENT_TYPE = 'audio/mpeg'
PHONE_CONTENT_TYPE = 'text/plain'

VOICE_TEXT_PATH = '/voice_text'
