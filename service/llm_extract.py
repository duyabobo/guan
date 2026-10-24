#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""用火山方舟抽出资料和期望。语音和提示词同一次送入，不再先转写成文字。"""
import base64
import json
import logging

from service.common.profile_catalog import extraction_hint
from util.config import get_conf
from util.const.volc import (
    ARK_API_BASE,
    ARK_AUDIO_FORMAT,
    ARK_AUDIO_MAX_TOKENS,
    ARK_AUDIO_TIMEOUT_SECONDS,
    ARK_MAX_TOKENS,
    ARK_MODEL,
    ARK_TEMPERATURE,
    ARK_THINKING_DISABLED,
    ARK_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)

_CONF_SECTION = 'volc'
_ARK_CLIENTS = {}

_EXTRACT_GUIDE = """
请提取婚恋匹配配置，只返回 JSON。
1. "transcript"：听到或读到的原话，不要润色。没有内容就用空字符串。
2. "my_info"：本人信息，只使用下面目录里的个人信息字段。
3. "my_requirement"：对对方的期望，只使用下面目录里的个人期望字段。

只提取明确提到的字段，未提及的不要猜测。选项用目录里的数字。
可提取维度（键名必须一致，未在目录中的键不要返回）：
{fields}
返回格式示例：
{{
  "transcript": "我是1995年的男生，身高170",
  "my_info": {{"sex": 1, "birth_year": 1995, "height": 170}},
  "my_requirement": {{"min_height": 165, "max_height": 185}}
}}

sex 字段值：1=男，2=女。
"""


class LlmExtractService:

    @staticmethod
    def extractMatchConfig(text):
        if not text:
            return None
        prompt = _EXTRACT_GUIDE.format(fields=extraction_hint()) + "\n文字如下：\n" + text
        return _extract([{'role': 'user', 'content': prompt}], ARK_MAX_TOKENS, ARK_TIMEOUT_SECONDS)

    @staticmethod
    def extract_from_audio(audio_bytes):
        if not audio_bytes:
            return None
        prompt = _EXTRACT_GUIDE.format(fields=extraction_hint())
        messages = [{'role': 'user', 'content': audio_user_content(audio_bytes, prompt)}]
        logger.info("提交语音提取 bytes=%s", len(audio_bytes))
        return _extract(messages, ARK_AUDIO_MAX_TOKENS, ARK_AUDIO_TIMEOUT_SECONDS)


def parse_extract_json(content):
    text = _strip_fence(content)
    data = _loads_object(text)
    if data is None:
        raise json.JSONDecodeError('extract result is not an object', text, 0)
    return data


def _strip_fence(content):
    text = (content or '').strip()
    if not text.startswith('```'):
        return text
    lines = text.splitlines()
    if lines and lines[0].startswith('```'):
        lines = lines[1:]
    if lines and lines[-1].startswith('```'):
        lines = lines[:-1]
    return '\n'.join(lines).strip()


def _loads_object(text):
    data = _loads_dict(text)
    if data is not None:
        return data
    start = text.find('{')
    end = text.rfind('}')
    if start < 0 or end <= start:
        return None
    return _loads_dict(text[start:end + 1])


def _loads_dict(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        return data
    return None


def audio_user_content(audio_bytes, prompt):
    """同一次用户消息里放语音和提示词。data 为标准 Base64，format 在使用 data 时必填。"""
    encoded = base64.b64encode(audio_bytes).decode('ascii')
    return [
        {
            'type': 'input_audio',
            'input_audio': {'data': encoded, 'format': ARK_AUDIO_FORMAT},
        },
        {'type': 'text', 'text': prompt},
    ]


def _extract(messages, max_tokens, timeout):
    api_key = get_conf('volc_ark_api_key', '', _CONF_SECTION).strip()
    if not api_key:
        logger.warning("火山方舟密钥未配置，跳过提取")
        return None
    content = _chat(api_key, messages, max_tokens, timeout)
    if not content:
        return None
    try:
        data = parse_extract_json(content)
    except json.JSONDecodeError:
        logger.warning("提取结果不是 JSON text_length=%s", len(content))
        return None
    logger.info("资料提取完成 text_length=%s", len(content))
    return data


def _chat(api_key, messages, max_tokens, timeout):
    api_base = get_conf('volc_ark_api_base', ARK_API_BASE, _CONF_SECTION).strip() or ARK_API_BASE
    model = get_conf('volc_ark_model', ARK_MODEL, _CONF_SECTION).strip() or ARK_MODEL
    try:
        response = _client(api_key, api_base).chat.completions.create(
            model=model,
            messages=messages,
            temperature=ARK_TEMPERATURE,
            max_tokens=max_tokens,
            timeout=timeout,
            extra_body={'thinking': {'type': ARK_THINKING_DISABLED}},
        )
    except Exception as exc:
        logger.warning("资料提取请求失败 model=%s error=%s", model, type(exc).__name__)
        return ''
    message = response.choices[0].message.content if response.choices else ''
    return (message or '').strip()


def _client(api_key, api_base):
    marker = (api_base, api_key)
    client = _ARK_CLIENTS.get(marker)
    if client is not None:
        return client
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=api_base, timeout=ARK_AUDIO_TIMEOUT_SECONDS, max_retries=0)
    _ARK_CLIENTS[marker] = client
    return client
