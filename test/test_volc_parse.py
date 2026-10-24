#! /usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.asr import flash_body, flash_headers, text_from_flash
from service.llm_extract import audio_user_content, parse_extract_json
from util.const.volc import (
    ARK_AUDIO_FORMAT,
    ASR_MODEL_NAME,
    ASR_RESOURCE_ID,
    ASR_STATUS_OK,
    ASR_STATUS_SILENCE,
)


def test_flash_headers_prefer_api_key():
    headers = flash_headers('new-key', 'app', 'token', 'req-1')
    assert headers['X-Api-Key'] == 'new-key'
    assert headers['X-Api-Resource-Id'] == ASR_RESOURCE_ID
    assert 'X-Api-App-Key' not in headers


def test_flash_headers_use_old_console_pair():
    headers = flash_headers('', 'app-id', 'access-token', 'req-2')
    assert headers['X-Api-App-Key'] == 'app-id'
    assert headers['X-Api-Access-Key'] == 'access-token'
    assert 'X-Api-Key' not in headers


def test_flash_headers_missing_credentials():
    assert flash_headers('', 'only-app', '', 'req-3') is None
    assert flash_headers('', '', '', 'req-4') is None


def test_flash_body_sends_audio_inline():
    body = flash_body(b'audio')
    assert body['audio']['format'] == 'mp3'
    assert 'url' not in body['audio']
    assert base64.b64decode(body['audio']['data']) == b'audio'
    assert body['request']['model_name'] == ASR_MODEL_NAME


def test_text_from_flash_reads_result():
    payload = {'result': {'text': ' 一九九五年  '}}
    assert text_from_flash(ASR_STATUS_OK, payload) == '一九九五年'


def test_text_from_flash_silence_is_empty():
    assert text_from_flash(ASR_STATUS_SILENCE, {'result': {'text': '噪声'}}) == ''
    assert text_from_flash('45000001', {'result': {'text': '坏参数'}}) == ''


def test_audio_user_content_sends_voice_and_prompt_together():
    parts = audio_user_content(b'audio', '提取资料')
    assert parts[0]['type'] == 'input_audio'
    assert parts[0]['input_audio']['format'] == ARK_AUDIO_FORMAT
    assert base64.b64decode(parts[0]['input_audio']['data']) == b'audio'
    assert parts[1] == {'type': 'text', 'text': '提取资料'}


def test_parse_extract_json_plain_and_fenced():
    plain = '{"my_info": {"sex": 1}, "my_requirement": {}}'
    assert parse_extract_json(plain)['my_info']['sex'] == 1
    fenced = "```json\n" + plain + "\n```"
    assert parse_extract_json(fenced)['my_info']['sex'] == 1


def test_parse_extract_json_rejects_non_object():
    with pytest.raises(json.JSONDecodeError):
        parse_extract_json('[1, 2]')
    with pytest.raises(json.JSONDecodeError):
        parse_extract_json('不是json')
