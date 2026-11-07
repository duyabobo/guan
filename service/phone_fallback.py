#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""用通行证上的手机号密文发短信。没配短信地址就只记日志。"""
import logging

from model.passport import PassportModel
from service.identity.runtime_key import materials_for
from util.const.identity import PURPOSE_PHONE_NOTIFY
from util.const.notice import notice_sms_text
from util.sensitive_cipher import open_phone_or_none
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
    sealed = PassportModel.phone_ciphers(passport_ids)
    if not sealed:
        return {}
    materials = materials_for(list(sealed.keys()), PURPOSE_PHONE_NOTIFY)
    found = {}
    for passport_id, stored in sealed.items():
        number = _open_number(passport_id, stored, materials.get(passport_id, ''))
        if number:
            found[passport_id] = number
    return found


def _open_number(passport_id, stored, material):
    number = open_phone_or_none(material, stored)
    if number is None:
        if material:
            logger.info("手机兜底解密失败 passport=%s", passport_id)
        else:
            logger.info("手机兜底缺少密钥 passport=%s", passport_id)
        return ''
    return number


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
