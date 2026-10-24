#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""用身份密钥材料做 AES-256-GCM。材料本身不写日志。"""
import base64
import hashlib
import hmac
import json
import secrets

from util.const.identity import (
    AES_KEY_BYTES,
    AES_NONCE_BYTES,
    AES_TAG_BYTES,
    HKDF_INFO,
    HKDF_SALT,
    UNION_SEAL_PREFIX,
)

_UNION_LOOKUP_INFO = b'guan-unionid-lookup-v1'
_JSON_SEPARATORS = (',', ':')

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


def union_lookup(unionid):
    """用 unionid 自己做 HMAC，得到不可反推的查找值。"""
    if not unionid:
        raise ValueError('empty key material')
    text = unionid.encode('utf-8') if isinstance(unionid, str) else unionid
    return hmac.new(text, _UNION_LOOKUP_INFO, hashlib.sha256).hexdigest()


def seal_unionid(unionid):
    """unionid 用自己加密后再落库。随机 nonce，不能拿来查找。"""
    if not unionid:
        raise ValueError('empty key material')
    nonce, packed = encrypt(unionid, unionid.encode('utf-8'))
    return UNION_SEAL_PREFIX + nonce + '.' + base64.b64encode(packed).decode('ascii')


def is_sealed_unionid(stored):
    return bool(stored) and str(stored).startswith(UNION_SEAL_PREFIX)


def stored_unionid_accepts(stored, unionid):
    """封存值必须能用这次微信返回的 unionid 解开。旧明文只做一次等值比对。"""
    if not stored or not unionid:
        return False
    if is_sealed_unionid(stored):
        return unionid_matches(unionid, stored)
    return _same_text(str(stored), unionid)


def unionid_matches(unionid, stored):
    body = str(stored or '')[len(UNION_SEAL_PREFIX):]
    nonce, packed = unpack_token(body)
    if not nonce or not packed:
        return False
    try:
        plain = decrypt(unionid, nonce, packed)
    except (ValueError, UnicodeDecodeError):
        return False
    return _same_text(plain.decode('utf-8'), unionid)


def seal_json(secret_material, payload):
    plain = json.dumps(payload, ensure_ascii=False, separators=_JSON_SEPARATORS).encode('utf-8')
    return encrypt(secret_material, plain)


def open_json(secret_material, nonce_text, packed):
    plain = decrypt(secret_material, nonce_text, packed)
    return json.loads(plain.decode('utf-8'))


def pack_token(nonce_text, packed):
    return nonce_text + '.' + base64.b64encode(_as_bytes(packed)).decode('ascii')


def unpack_token(stored):
    nonce, dot, cipher_b64 = str(stored or '').partition('.')
    if not dot or not nonce or not cipher_b64:
        return '', b''
    try:
        return nonce, base64.b64decode(cipher_b64)
    except ValueError:
        return '', b''


def _same_text(left, right):
    left = left or ''
    right = right or ''
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left, right)


def _as_bytes(value):
    if isinstance(value, bytes):
        return value
    return bytes(value)
