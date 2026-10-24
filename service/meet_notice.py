#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""订阅额度，以及把见面提醒发给已经授权的人。"""
import logging

from model.activity import ActivityModel
from model.notice_sent import NoticeSentModel
from model.subscribe_grant import SubscribeGrantModel
from service.common.notice_due import drop_sent, scheduled_notices
from service.identity.runtime_key import material_for, materials_for
from service.meet_fee import openid_belongs_to
from service.phone_fallback import deliver_missed
from util.const.identity import PURPOSE_SUBSCRIBE_SEND
from util.const.notice import (
    LIST_EXPIRE_LEAD,
    MEET_PAGE,
    MEET_SOON_LEAD,
    NOTICE_TEXT,
    SCAN_ACTIVITY_LIMIT,
    SUBSCRIBE_ACCEPT,
)
from util.const.progress import MEET_AUTO_FIT_WAIT
from util.sensitive_cipher import decrypt, encrypt
from util.wx_subscribe import build_data, miniprogram_state, send_subscribe, template_id

logger = logging.getLogger(__name__)


def page_subscribe(viewer):
    if viewer:
        return {'templateIds': []}
    return {'templateIds': [template_id()]}


def subscription_accepted(subscribe_res, template):
    if not isinstance(subscribe_res, dict) or not template:
        return False
    return subscribe_res.get(template) == SUBSCRIBE_ACCEPT


class MeetNoticeService(object):

    @staticmethod
    def accept(passport_id, openid, subscribe_res):
        template = template_id()
        if not subscription_accepted(subscribe_res, template):
            logger.info("订阅未授权 passport=%s", passport_id)
            return
        if not openid_belongs_to(passport_id, openid):
            logger.info("订阅未记下 passport=%s openid 与账号不一致", passport_id)
            return
        material = material_for(passport_id, PURPOSE_SUBSCRIBE_SEND)
        if not material:
            logger.info("订阅未记下 passport=%s 没有身份密钥", passport_id)
            return
        nonce, cipher_bytes = encrypt(material, openid.encode('utf-8'))
        SubscribeGrantModel.grant(passport_id, template, nonce, cipher_bytes)

    @staticmethod
    def dispatch(jobs, record_sent):
        jobs = [job for job in jobs if job and job.passport_id and job.start_time]
        if not jobs:
            return
        try:
            _dispatch(jobs, record_sent)
        except Exception:
            logger.exception("见面提醒发送失败 count=%s", len(jobs))

    @staticmethod
    def scan(now):
        decide_start = now - MEET_AUTO_FIT_WAIT
        rows = ActivityModel.list_notice_candidates(
            now, decide_start, now + MEET_SOON_LEAD, now + LIST_EXPIRE_LEAD, SCAN_ACTIVITY_LIMIT,
        )
        if len(rows) >= SCAN_ACTIVITY_LIMIT:
            logger.info("见面提醒扫描达到上限 limit=%s", SCAN_ACTIVITY_LIMIT)
        jobs = []
        for row in rows:
            jobs.extend(scheduled_notices(row, now))
        sent = NoticeSentModel.sent_keys_for([row.id for row in rows])
        MeetNoticeService.dispatch(drop_sent(jobs, sent), record_sent=True)


def _dispatch(jobs, record_sent):
    template = template_id()
    passport_ids = list({job.passport_id for job in jobs})
    grants = SubscribeGrantModel.map_by_passports(passport_ids, template)
    materials = materials_for(passport_ids, PURPOSE_SUBSCRIBE_SEND)
    openids = _openids(grants, materials)
    state = miniprogram_state()
    usable = {}
    for passport_id, grant in grants.items():
        usable[passport_id] = grant.remain or 0
    used = {}
    sent_jobs = []
    missed = []
    for job in jobs:
        left = usable.get(job.passport_id, 0) - used.get(job.passport_id, 0)
        openid = openids.get(job.passport_id)
        if left <= 0 or not openid:
            missed.append(job)
            continue
        data = build_data(job.scene, job.start_time, NOTICE_TEXT, job.note)
        sent = send_subscribe(openid, template, MEET_PAGE % job.activity_id, data, state)
        if not sent:
            missed.append(job)
            continue
        used[job.passport_id] = used.get(job.passport_id, 0) + 1
        sent_jobs.append(job)
    for passport_id, count in used.items():
        SubscribeGrantModel.consume_remain(passport_id, template, count)
    sent_jobs.extend(deliver_missed(missed))
    if record_sent:
        NoticeSentModel.add_jobs(sent_jobs)
    logger.info("见面提醒 sent=%s missed=%s", len(sent_jobs), len(missed))


def _openids(grants, materials):
    found = {}
    for passport_id, grant in grants.items():
        material = materials.get(passport_id)
        if not material or not grant.openid_nonce or not grant.openid_cipher:
            continue
        try:
            plain = decrypt(material, grant.openid_nonce, grant.openid_cipher)
        except Exception:
            logger.info("订阅 openid 解不开 passport=%s", passport_id)
            continue
        if isinstance(plain, bytes):
            plain = plain.decode('utf-8')
        found[passport_id] = plain
    return found
