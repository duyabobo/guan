#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""订阅消息发不出去时，用已绑定手机号发短信。没配短信地址就只记日志。"""
import json
import logging
from urllib import request as urlrequest

from model.identity_secret import IdentitySecretModel
from model.sensitive_record import SensitiveRecordModel
from util.config import get_conf
from util.const.identity import KIND_PHONE, PROVIDER_WECHAT, PURPOSE_PHONE_NOTIFY
from util.const.notice import WX_HTTP_TIMEOUT_SEC, notice_sms_text
from util.sensitive_cipher import decrypt
from util.wx_http import path_of

logger = logging.getLogger(__name__)

SMS_SECTION = 'sms'
SMS_URL_KEY = 'sms_url'
SMS_TOKEN_KEY = 'sms_token'
SMS_TOKEN_HEADER = 'X-Sms-Token'


def deliver_missed(jobs):
    if not jobs:
        return []
    url = get_conf(SMS_URL_KEY, '', SMS_SECTION)
    if not url:
        logger.info("手机兜底未发出 count=%s 未配置短信", len(jobs))
        return []
    token = get_conf(SMS_TOKEN_KEY, '', SMS_SECTION)
    numbers = _bound_numbers([job.passport_id for job in jobs])
    outbound, missing = _outbound(jobs, numbers)
    sent = _deliver(url, token, outbound)
    failed = len(outbound) - len(sent)
    logger.info(
        "手机兜底 sent=%s missing=%s failed=%s",
        len(sent), missing, failed,
    )
    return sent


def _bound_numbers(passport_ids):
    records = SensitiveRecordModel.latest_map(passport_ids, KIND_PHONE)
    if not records:
        return {}
    materials = IdentitySecretModel.load_materials(
        list(records.keys()), PROVIDER_WECHAT, PURPOSE_PHONE_NOTIFY,
    )
    found = {}
    for passport_id, record in records.items():
        number = _open_number(passport_id, record, materials.get(passport_id, ''))
        if number:
            found[passport_id] = number
    return found


def _open_number(passport_id, record, material):
    if record.key_provider != PROVIDER_WECHAT or not material:
        logger.info("手机兜底缺少密钥 passport=%s", passport_id)
        return ''
    try:
        plain = decrypt(material, record.nonce, record.cipher_text)
        if isinstance(plain, bytes):
            plain = plain.decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        logger.info("手机兜底解密失败 passport=%s", passport_id)
        return ''
    return plain or ''


def _outbound(jobs, numbers):
    outbound = []
    missing = 0
    for job in jobs:
        number = numbers.get(job.passport_id, '')
        if not number:
            missing += 1
            continue
        outbound.append({
            'job': job,
            'phone': number,
            'text': notice_sms_text(job.scene, job.start_time, job.note),
        })
    return outbound, missing


def _deliver(url, token, outbound):
    if not outbound:
        return []
    messages = [{'phone': item['phone'], 'text': item['text']} for item in outbound]
    if not _post_sms(url, token, messages):
        return []
    return [item['job'] for item in outbound]


def _post_sms(url, token, messages):
    logger.info("请求短信 path=%s count=%s", path_of(url), len(messages))
    headers = {'Content-Type': 'application/json'}
    if token:
        headers[SMS_TOKEN_HEADER] = token
    body = json.dumps({'messages': messages}, ensure_ascii=False).encode('utf-8')
    req = urlrequest.Request(url, data=body, headers=headers)
    try:
        with urlrequest.urlopen(req, timeout=WX_HTTP_TIMEOUT_SEC) as resp:
            return 200 <= resp.status < 300
    except Exception:
        logger.exception("手机兜底发送失败")
        return False
