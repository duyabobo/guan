#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.const.identity import AES_KEY_BYTES
from util.sensitive_cipher import decrypt, derive_key, encrypt


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


def test_empty_plain_rejected():
    failed = False
    try:
        encrypt('union', b'')
    except ValueError:
        failed = True
    assert failed
