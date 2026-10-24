#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.const.identity import AES_KEY_BYTES
from util.sensitive_cipher import (
    decrypt,
    derive_key,
    encrypt,
    is_sealed_unionid,
    open_json,
    seal_json,
    seal_unionid,
    stored_unionid_accepts,
    union_lookup,
    unionid_matches,
)


def test_same_material_same_key():
    assert derive_key('union-1') == derive_key('union-1')
    assert derive_key('union-1') != derive_key('union-2')
    assert len(derive_key('union-1')) == AES_KEY_BYTES


def test_roundtrip():
    plain = b'\x00\x01voice-bytes'
    nonce, cipher = encrypt('union-id-example', plain)
    assert decrypt('union-id-example', nonce, cipher) == plain


def test_encrypt_is_not_deterministic():
    first = encrypt('union', b'same')
    second = encrypt('union', b'same')
    assert first != second


def test_other_material_cannot_decrypt():
    nonce, cipher = encrypt('union-a', b'voice')
    failed = False
    try:
        decrypt('union-b', nonce, cipher)
    except ValueError:
        failed = True
    assert failed


def test_empty_material_rejected():
    failed = False
    try:
        encrypt('', b'voice')
    except ValueError:
        failed = True
    assert failed


def test_unionid_seal_hides_plaintext_and_roundtrips():
    unionid = 'oUnionIdExampleValue'
    sealed = seal_unionid(unionid)
    assert is_sealed_unionid(sealed)
    assert unionid not in sealed
    assert unionid_matches(unionid, sealed)
    assert stored_unionid_accepts(sealed, unionid)
    assert stored_unionid_accepts(unionid, unionid)
    assert not stored_unionid_accepts(sealed, 'other-union')
    assert union_lookup(unionid) == union_lookup(unionid)
    assert union_lookup(unionid) != union_lookup('other-union')
    assert unionid not in union_lookup(unionid)


def test_json_seal_roundtrip():
    nonce, cipher = seal_json('union-id', {'value_min': 1996, 'value_text': '北京'})
    assert open_json('union-id', nonce, cipher)['value_text'] == '北京'


def test_empty_plain_rejected():
    failed = False
    try:
        encrypt('union', b'')
    except ValueError:
        failed = True
    assert failed
