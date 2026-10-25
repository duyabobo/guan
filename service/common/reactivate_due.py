#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""沉默用户眼前有匹配的邀请时，生成一条促活提醒。不访问数据库。"""
from service.common.notice_due import NoticeJob
from service.common.profile_match import inviter_passport_id, requirement_accepts
from service.common.profile_rows import missing_required_info_keys
from util.const.match import (
    MODEL_ACTIVITY_STATE_INVITING,
    MODEL_SEX_FEMALE_INDEX,
    MODEL_SEX_MALE_INDEX,
)
from util.const.notice import HOME_PAGE, SCENE_REACTIVATE
from util.const.progress import (
    HEART_KIND_SINGLE,
    calc_distance_km,
    should_show_guanguan_item,
)

_KNOWN_SEX = (MODEL_SEX_MALE_INDEX, MODEL_SEX_FEMALE_INDEX)
SECONDS_PER_MINUTE = 60


class ReactivateViewer(object):
    def __init__(self, passport_id, latitude, longitude, info_map):
        self.passport_id = passport_id
        self.latitude = latitude
        self.longitude = longitude
        self.info_map = info_map or {}


def pick_reactivate_jobs(viewers, activities, profiles, address_of, now):
    slots = [activity for activity in activities or [] if _open_inviting(activity)]
    jobs = []
    for viewer in viewers or []:
        job = _job_for(viewer, slots, profiles or {}, address_of or {}, now)
        if job:
            jobs.append(job)
    return jobs


def drop_cooled(jobs, cooled_passport_ids):
    cooled = set(cooled_passport_ids or [])
    return [job for job in jobs or [] if job.passport_id not in cooled]


def _job_for(viewer, activities, profiles, address_of, now):
    if missing_required_info_keys(viewer.info_map):
        return None
    sex = _sex(viewer.info_map)
    if sex not in _KNOWN_SEX:
        return None
    chosen = None
    for activity in activities:
        if not _fits(viewer, sex, activity, profiles, address_of, now):
            continue
        if chosen is None or activity.start_time < chosen.start_time:
            chosen = activity
    if chosen is None:
        return None
    return NoticeJob(viewer.passport_id, SCENE_REACTIVATE, chosen.id, chosen.start_time, page=HOME_PAGE)


def _fits(viewer, sex, activity, profiles, address_of, now):
    inviter_id = inviter_passport_id(activity)
    if not inviter_id or inviter_id == viewer.passport_id:
        return False
    if inviter_id not in profiles or _empty_seat_sex(activity) != sex:
        return False
    inviter = profiles.get(inviter_id) or {}
    if not requirement_accepts(viewer.info_map, inviter.get('requirement') or {}):
        return False
    address = address_of.get(activity.address_id)
    if not address:
        return False
    distance_km = calc_distance_km(
        viewer.latitude, viewer.longitude, address.latitude, address.longitude,
    )
    minutes_until = (activity.start_time - now).total_seconds() / SECONDS_PER_MINUTE
    return should_show_guanguan_item(HEART_KIND_SINGLE, distance_km, minutes_until)


def _open_inviting(activity):
    if getattr(activity, 'seat_locked', False):
        return False
    if activity.state != MODEL_ACTIVITY_STATE_INVITING or not activity.start_time:
        return False
    return bool(inviter_passport_id(activity))


def _empty_seat_sex(activity):
    boy_id = activity.boy_passport_id or 0
    girl_id = activity.girl_passport_id or 0
    if boy_id and not girl_id:
        return MODEL_SEX_FEMALE_INDEX
    if girl_id and not boy_id:
        return MODEL_SEX_MALE_INDEX
    return 0


def _sex(info_map):
    row = (info_map or {}).get('sex')
    if row is None:
        return 0
    return row.value_min or 0
