#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""用已绑定手机号发短信。没配短信地址就只记日志。"""
import logging

from model.sensitive_record import SensitiveRecordModel
from service.identity.runtime_key import materials_for
from util.const.identity import KIND_PHONE, PROVIDER_WECHAT, PURPOSE_PHONE_NOTIFY
from util.const.notice import notice_sms_text
from util.sensitive_cipher import decrypt
from util.sms_gateway import post_messages, sms_configured

logger = logging.getLogger(__name__)


def deliver_missed(jobs):
    if not jobs:
        return []
    if not sms_configured():
        logger.info("手机兜底未发出 count=%s 未配置短信", len(jobs))
        return []
    numbers = _bound_numbers([job.passport_id for job in jobs])
    outbound, missing = _outbound(jobs, numbers)
    sent = _deliver(outbound)
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
    materials = materials_for(list(records.keys()), PURPOSE_PHONE_NOTIFY)
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


def _deliver(outbound):
    if not outbound:
        return []
    messages = [{'phone': item['phone'], 'text': item['text']} for item in outbound]
    if not post_messages(messages):
        return []
    return [item['job'] for item in outbound]
