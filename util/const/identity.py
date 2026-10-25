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
PURPOSE_PROFILE = 'profile_store'
PURPOSE_MEET_SEAT = 'meet_seat'
PURPOSE_PHONE_CODE = 'phone_code'
PURPOSE_MIN_LENGTH = 4

# 真实 unionid 只放 Redis。会话令牌换前缀后，旧的可猜测令牌全部失效。
RUNTIME_UNION_TTL_SEC = 90 * 24 * 3600
RUNTIME_UNION_KEY = 'runtime_union:%s'
SESSION_KEY_PREFIX = 'accessToken:v2:'
LOGIN_PATH = '/login'
UNION_SEAL_PREFIX = 'guan-seal-v1:'

MAX_VOICE_BYTES = 5 * 1024 * 1024
MAX_VOICE_TEXT_CHARS = 2000  # 文字版提取同样要限长：全文会拼进提示词发给大模型
VOICE_CONTENT_TYPE = 'audio/mpeg'
PHONE_CONTENT_TYPE = 'text/plain'

VOICE_TEXT_PATH = '/voice_text'
