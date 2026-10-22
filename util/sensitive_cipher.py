#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""用身份密钥材料做 AES-256-GCM。材料本身不写日志。"""
import base64
import hashlib
import hmac
import secrets

from util.const.identity import (
    AES_KEY_BYTES,
    AES_NONCE_BYTES,
    AES_TAG_BYTES,
    HKDF_INFO,
    HKDF_SALT,
)

_HKDF_COUNTER_LIMIT = hashlib.sha256().digest_size


def derive_key(secret_material):
    """HKDF-SHA256。同一材料每次得到同一把 AES 密钥。"""
    if not secret_material:
        raise ValueError('empty key material')
    ikm = secret_material.encode('utf-8') if isinstance(secret_material, str) else secret_material
    prk = hmac.new(HKDF_SALT, ikm, hashlib.sha256).digest()
    okm = b''
    previous = b''
    counter = 1
    while len(okm) < AES_KEY_BYTES:
        previous = hmac.new(prk, previous + HKDF_INFO + bytes([counter]), hashlib.sha256).digest()
        okm += previous
        counter += 1
        if counter > _HKDF_COUNTER_LIMIT:
            raise ValueError('hkdf counter exhausted')
    return okm[:AES_KEY_BYTES]


def encrypt(secret_material, plain):
    if not plain:
        raise ValueError('empty plain')
    nonce = secrets.token_bytes(AES_NONCE_BYTES)
    cipher = _aes(secret_material, nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plain)
    nonce_text = base64.b64encode(nonce).decode('ascii')
    return nonce_text, ciphertext + tag


def decrypt(secret_material, nonce_text, packed):
    packed = _as_bytes(packed)
    if len(packed) <= AES_TAG_BYTES:
        raise ValueError('cipher too short')
    nonce = base64.b64decode(nonce_text)
    if len(nonce) != AES_NONCE_BYTES:
        raise ValueError('bad nonce')
    cipher = _aes(secret_material, nonce)
    ciphertext = packed[:-AES_TAG_BYTES]
    tag = packed[-AES_TAG_BYTES:]
    return cipher.decrypt_and_verify(ciphertext, tag)


def _aes(secret_material, nonce):
    from Crypto.Cipher import AES
    return AES.new(derive_key(secret_material), AES.MODE_GCM, nonce=nonce)


def _as_bytes(value):
    if isinstance(value, bytes):
        return value
    return bytes(value)
