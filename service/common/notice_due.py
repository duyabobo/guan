#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""哪些到点提醒该发。不访问数据库。"""
import datetime

from service.common.profile_match import inviter_passport_id, seated_passport_ids
from util.const.match import MODEL_ACTIVITY_STATE_INVITE_SUCCESS, MODEL_ACTIVITY_STATE_INVITING
from util.const.notice import (
    LIST_EXPIRE_LEAD,
    MEET_ARRIVE_WINDOW,
    MEET_SOON_LEAD,
    SCENE_DECIDE,
    SCENE_LIST_EXPIRE,
    SCENE_MEET_ARRIVE,
    SCENE_MEET_SOON,
)
from util.const.progress import MEET_AUTO_FIT_WAIT, MEET_CHOICE_WAIT


class NoticeJob(object):
    def __init__(self, passport_id, scene, activity_id, start_time, note='', page=''):
        self.passport_id = passport_id
        self.scene = scene
        self.activity_id = activity_id
        self.start_time = start_time
        self.note = note or ''
        self.page = page or ''


def _results_unset(activity):
    return not activity.boy_meet_result and not activity.girl_meet_result


def _until(activity, now):
    if not activity.start_time:
        return None
    return activity.start_time - now


def scheduled_notices(activity, now):
    """一场在这一刻该发给谁。已经发过的由调用方去掉。"""
    jobs = []
    jobs.extend(_list_expire_jobs(activity, now))
    jobs.extend(_meet_soon_jobs(activity, now))
    jobs.extend(_meet_arrive_jobs(activity, now))
    jobs.extend(_decide_jobs(activity, now))
    return jobs


def _list_expire_jobs(activity, now):
    if activity.state != MODEL_ACTIVITY_STATE_INVITING:
        return []
    remaining = _until(activity, now)
    if remaining is None or remaining <= datetime.timedelta(0) or remaining > LIST_EXPIRE_LEAD:
        return []
    inviter_id = inviter_passport_id(activity)
    if not inviter_id:
        return []
    return [NoticeJob(inviter_id, SCENE_LIST_EXPIRE, activity.id, activity.start_time)]


def _meet_soon_jobs(activity, now):
    if activity.state != MODEL_ACTIVITY_STATE_INVITE_SUCCESS or not _results_unset(activity):
        return []
    remaining = _until(activity, now)
    if remaining is None or remaining <= datetime.timedelta(0) or remaining > MEET_SOON_LEAD:
        return []
    return _for_each_seated(activity, SCENE_MEET_SOON)


def _meet_arrive_jobs(activity, now):
    if activity.state != MODEL_ACTIVITY_STATE_INVITE_SUCCESS or not _results_unset(activity):
        return []
    if not activity.start_time:
        return []
    elapsed = now - activity.start_time
    if elapsed < datetime.timedelta(0) or elapsed > MEET_ARRIVE_WINDOW:
        return []
    return _for_each_seated(activity, SCENE_MEET_ARRIVE)


def _decide_jobs(activity, now):
    if activity.state != MODEL_ACTIVITY_STATE_INVITE_SUCCESS or not _results_unset(activity):
        return []
    if not activity.start_time:
        return []
    if now < activity.start_time + MEET_CHOICE_WAIT:
        return []
    if now >= activity.start_time + MEET_AUTO_FIT_WAIT:
        return []
    return _for_each_seated(activity, SCENE_DECIDE)


def _for_each_seated(activity, scene):
    return [
        NoticeJob(passport_id, scene, activity.id, activity.start_time)
        for passport_id in seated_passport_ids(activity)
    ]


def sent_key(activity_id, passport_id, scene):
    return (activity_id, passport_id, scene)


def drop_sent(jobs, sent_keys):
    pending = []
    for job in jobs:
        if sent_key(job.activity_id, job.passport_id, job.scene) in sent_keys:
            continue
        pending.append(job)
    return pending
