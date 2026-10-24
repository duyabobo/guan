#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""豆包语音录音文件极速版。音频直接随请求上传，一次返回识别文本。"""
import base64
import json
import logging
import uuid
import urllib.error
import urllib.request

from util.config import get_conf
from util.const.volc import (
    ASR_AUDIO_FORMAT,
    ASR_EMPTY_STATUSES,
    ASR_FLASH_URL,
    ASR_LANGUAGE,
    ASR_MODEL_NAME,
    ASR_RESOURCE_ID,
    ASR_SEQUENCE,
    ASR_STATUS_OK,
    ASR_TIMEOUT_SECONDS,
    ASR_USER_ID,
)

logger = logging.getLogger(__name__)

_CONF_SECTION = 'volc'


class AsrService(object):

    def transcribe(self, audio_bytes):
        if not audio_bytes:
            return ''
        headers = flash_headers(
            get_conf('volc_asr_api_key', '', _CONF_SECTION),
            get_conf('volc_asr_app_key', '', _CONF_SECTION),
            get_conf('volc_asr_access_key', '', _CONF_SECTION),
            uuid.uuid4().hex,
        )
        if not headers:
            logger.warning("火山语音密钥未配置，跳过识别")
            return ''
        request_id = headers['X-Api-Request-Id']
        logger.info("提交语音识别 bytes=%s request_id=%s", len(audio_bytes), request_id)
        status, message, payload, logid = _post_flash(headers, flash_body(audio_bytes))
        text = text_from_flash(status, payload)
        logger.info(
            "语音识别返回 status=%s message=%s logid=%s text_length=%s request_id=%s",
            status, message, logid, len(text), request_id,
        )
        return text


def flash_headers(api_key, app_key, access_key, request_id):
    """新版控制台用 API Key。旧版用 AppID 加 Access Token。两套都空则无法调用。"""
    api_key = (api_key or '').strip()
    app_key = (app_key or '').strip()
    access_key = (access_key or '').strip()
    if not api_key and not (app_key and access_key):
        return None
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Resource-Id': ASR_RESOURCE_ID,
        'X-Api-Request-Id': request_id,
        'X-Api-Sequence': ASR_SEQUENCE,
    }
    if api_key:
        headers['X-Api-Key'] = api_key
        return headers
    headers['X-Api-App-Key'] = app_key
    headers['X-Api-Access-Key'] = access_key
    return headers


def flash_body(audio_bytes):
    return {
        'user': {'uid': ASR_USER_ID},
        'audio': {
            'data': base64.b64encode(audio_bytes).decode('ascii'),
            'format': ASR_AUDIO_FORMAT,
            'language': ASR_LANGUAGE,
        },
        'request': {
            'model_name': ASR_MODEL_NAME,
            'enable_itn': True,
            'enable_punc': True,
        },
    }


def text_from_flash(status_code, payload):
    status = str(status_code or '')
    if status in ASR_EMPTY_STATUSES or status != ASR_STATUS_OK:
        return ''
    result = (payload or {}).get('result') or {}
    return (result.get('text') or '').strip()


def _post_flash(headers, body):
    raw = json.dumps(body).encode('utf-8')
    request = urllib.request.Request(ASR_FLASH_URL, data=raw, headers=headers, method='POST')
    try:
        response = urllib.request.urlopen(request, timeout=ASR_TIMEOUT_SECONDS)
    except urllib.error.HTTPError as exc:
        response = exc
    except urllib.error.URLError as exc:
        logger.warning("语音识别请求失败 request_id=%s error=%s", headers.get('X-Api-Request-Id'), exc.reason)
        return '', '', {}, ''
    try:
        return _read_flash(response)
    finally:
        response.close()


def _read_flash(response):
    status = response.headers.get('X-Api-Status-Code', '')
    message = response.headers.get('X-Api-Message', '')
    logid = response.headers.get('X-Tt-Logid', '')
    raw = response.read()
    if not raw:
        return status, message, {}, logid
    try:
        payload = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.warning("语音识别响应不是 JSON logid=%s", logid)
        return status, message, {}, logid
    if not isinstance(payload, dict):
        return status, message, {}, logid
    return status, message, payload, logid
