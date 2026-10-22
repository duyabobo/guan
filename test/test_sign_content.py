#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.encode import md5_hex
from util.sign_content import (
    content_from_query,
    encode_text,
    form_fields,
    sign_digest,
)


def test_sign_content_sorts_keys():
    left = content_from_query({"b": 1, "a": "x"})
    right = content_from_query({"a": "x", "b": 1})
    assert left == right
    assert left.index(encode_text("a")) < left.index(encode_text("b"))


def test_number_and_digit_string_encode_the_same():
    assert content_from_query(0) == content_from_query("0")


def test_sign_digest_drops_undefined_query_values():
    digest = sign_digest("/match_config", "PUT", "sign-secret", b"", "height=170&skip=undefined")
    params = {
        "secret": "sign-secret",
        "path": "/match_config",
        "method": "PUT",
        "height": "170",
    }
    assert digest == md5_hex(content_from_query(params))
    assert digest != sign_digest("/match_config", "PUT", "other-secret", b"", "height=170")


def test_json_body_participates_in_sign():
    body = b'{"sex":1,"birth_year":1996}'
    digest = sign_digest("/voice_text", "POST", "sign-secret", body, "")
    assert digest == md5_hex(content_from_query({
        "secret": "sign-secret",
        "path": "/voice_text",
        "method": "POST",
        "sex": 1,
        "birth_year": 1996,
    }))


def test_multipart_fields_keep_text_and_skip_empty():
    assert form_fields({"note": [b"hello"], "blank": []}) == {"note": "hello"}
    digest = sign_digest(
        "/voice_text", "POST", "sign-secret", b"", "",
        content_type="multipart/form-data; boundary=abc",
        form_arguments={"note": [b"hello"]},
    )
    assert digest == md5_hex(content_from_query({
        "secret": "sign-secret",
        "path": "/voice_text",
        "method": "POST",
        "note": "hello",
    }))
