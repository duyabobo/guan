#! /usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from service.llm_extract import audio_user_content, parse_extract_json
from util.const.volc import ARK_AUDIO_FORMAT


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
