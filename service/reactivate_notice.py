#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""有人已经坐在附近的场次里，而匹配的人好几天没来，就推一次，让他回来选时间地点。"""
import datetime
import logging

from model.activity import ActivityModel
from model.address import AddressModel
from model.notice_sent import NoticeSentModel
from model.passport import PassportModel
from model.profile_attr import ProfileAttrModel
from service.common.notice_due import drop_sent
from service.common.presence import idle_passport_ids, locations_of
from service.common.profile_catalog import SCOPE_INFO, SCOPE_REQUIREMENT
from service.common.profile_match import inviter_passport_id
from service.common.reactivate_due import drop_cooled, pick_reactivate_jobs, ReactivateViewer
from service.meet_notice import MeetNoticeService
from service.meet_seat import activity_ids_by_passport
from util.const.match import MODEL_ACTIVITY_STATE_INVITE_SUCCESS, MODEL_ACTIVITY_STATE_INVITING
from util.const.notice import (
    REACTIVATE_ACTIVITY_LIMIT,
    REACTIVATE_COOLDOWN,
    REACTIVATE_CURSOR_KEY,
    REACTIVATE_PASSPORT_LIMIT,
    SCENE_REACTIVATE,
)
from util.const.progress import MAX_TRANSIENT_LEAD_MINUTES, MEET_AUTO_FIT_WAIT
from util.redis_conn import decode_redis_value, redisConn

logger = logging.getLogger(__name__)


class ReactivateNoticeService(object):

    @staticmethod
    def scan(now):
        until = now + datetime.timedelta(minutes=MAX_TRANSIENT_LEAD_MINUTES)
        activities = ActivityModel.list_future_inviting(now, until, REACTIVATE_ACTIVITY_LIMIT)
        if len(activities) >= REACTIVATE_ACTIVITY_LIMIT:
            logger.info("促活场次达到上限 limit=%s", REACTIVATE_ACTIVITY_LIMIT)
        if not activities:
            logger.info("促活没有即将可见的邀请")
            return
        passport_ids = _next_passport_ids()
        idle_ids = idle_passport_ids(passport_ids)
        if not idle_ids:
            logger.info("促活本批没有沉默用户 scanned=%s", len(passport_ids))
            return
        jobs = _jobs_for(idle_ids, activities, now)
        pending = _pending(jobs, now)
        MeetNoticeService.dispatch(pending, record_sent=True)
        logger.info(
            "促活扫描 scanned=%s idle=%s jobs=%s pending=%s",
            len(passport_ids), len(idle_ids), len(jobs), len(pending),
        )


def _jobs_for(idle_ids, activities, now):
    seat_index = activity_ids_by_passport(idle_ids)
    history = ActivityModel.list_by_ids(_flat_ids(seat_index))
    history_by_id = {row.id: row for row in history}
    busy = _busy_ids(seat_index, history_by_id, now)
    quiet_ids = [passport_id for passport_id in idle_ids if passport_id not in busy]
    if not quiet_ids:
        logger.info("促活沉默用户都还在见面流程里 idle=%s", len(idle_ids))
        return []
    address_of = _address_of(_address_ids(activities, history))
    locations = _locations(quiet_ids, seat_index, history_by_id, address_of)
    located_ids = [passport_id for passport_id in quiet_ids if passport_id in locations]
    if not located_ids:
        logger.info("促活沉默用户没有位置 quiet=%s", len(quiet_ids))
        return []
    profiles = _group_profiles(ProfileAttrModel.listByPassportIds(_profile_ids(located_ids, activities)))
    viewers = _viewers(located_ids, locations, profiles)
    logger.info("促活可定位 quiet=%s located=%s", len(quiet_ids), len(located_ids))
    return pick_reactivate_jobs(viewers, activities, profiles, address_of, now)


def _pending(jobs, now):
    if not jobs:
        return []
    sent = NoticeSentModel.sent_keys_for([job.activity_id for job in jobs])
    cooled = NoticeSentModel.recent_passport_ids(
        [job.passport_id for job in jobs], SCENE_REACTIVATE, now - REACTIVATE_COOLDOWN,
    )
    return drop_cooled(drop_sent(jobs, sent), cooled)


def _next_passport_ids():
    after_id = _cursor()
    passport_ids = PassportModel.list_ids_after(after_id, REACTIVATE_PASSPORT_LIMIT)
    if len(passport_ids) < REACTIVATE_PASSPORT_LIMIT:
        redisConn.set(REACTIVATE_CURSOR_KEY, 0)
    else:
        redisConn.set(REACTIVATE_CURSOR_KEY, passport_ids[-1])
    logger.info("促活翻页 after=%s count=%s", after_id, len(passport_ids))
    return passport_ids


def _cursor():
    raw = decode_redis_value(redisConn.get(REACTIVATE_CURSOR_KEY))
    if raw and str(raw).isdigit():
        return int(raw)
    return 0


def _locations(passport_ids, seat_index, history_by_id, address_of):
    found = locations_of(passport_ids)
    for passport_id in passport_ids:
        if passport_id in found:
            continue
        point = _latest_point(seat_index.get(passport_id, []), history_by_id, address_of)
        if point:
            found[passport_id] = point
    return found


def _latest_point(activity_ids, history_by_id, address_of):
    best = None
    for activity_id in activity_ids:
        activity = history_by_id.get(activity_id)
        address = address_of.get(activity.address_id) if activity else None
        if not activity or not activity.start_time or not address:
            continue
        if best is None or activity.start_time > best[0]:
            best = (activity.start_time, address.latitude, address.longitude)
    if best is None:
        return None
    return best[1], best[2]


def _busy_ids(seat_index, history_by_id, now):
    horizon = now - MEET_AUTO_FIT_WAIT
    busy = set()
    for passport_id, activity_ids in seat_index.items():
        if _still_meeting(activity_ids, history_by_id, now, horizon):
            busy.add(passport_id)
    return busy


def _still_meeting(activity_ids, history_by_id, now, horizon):
    for activity_id in activity_ids:
        activity = history_by_id.get(activity_id)
        if activity and _in_meet(activity, now, horizon):
            return True
    return False


def _in_meet(activity, now, horizon):
    if not activity.start_time:
        return False
    if activity.state == MODEL_ACTIVITY_STATE_INVITING:
        return activity.start_time > now
    if activity.state == MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
        return activity.start_time > horizon
    return False


def _viewers(passport_ids, locations, profiles):
    viewers = []
    for passport_id in passport_ids:
        point = locations.get(passport_id)
        if not point:
            continue
        packed = profiles.get(passport_id) or {}
        viewers.append(ReactivateViewer(passport_id, point[0], point[1], packed.get('info')))
    return viewers


def _group_profiles(rows):
    grouped = {}
    for row in rows or []:
        packed = grouped.setdefault(row.passport_id, {'info': {}, 'requirement': {}})
        if row.scope == SCOPE_INFO:
            packed['info'][row.dim_key] = row
        elif row.scope == SCOPE_REQUIREMENT:
            packed['requirement'][row.dim_key] = row
    return grouped


def _profile_ids(passport_ids, activities):
    ids = list(passport_ids)
    seen = set(ids)
    for activity in activities:
        inviter_id = inviter_passport_id(activity)
        if inviter_id and inviter_id not in seen:
            seen.add(inviter_id)
            ids.append(inviter_id)
    return ids


def _address_ids(activities, history):
    ids = []
    seen = set()
    for activity in list(activities or []) + list(history or []):
        address_id = activity.address_id or 0
        if not address_id or address_id in seen:
            continue
        seen.add(address_id)
        ids.append(address_id)
    return ids


def _address_of(address_ids):
    if not address_ids:
        return {}
    return {row.id: row for row in AddressModel.listByIds(address_ids)}


def _flat_ids(seat_index):
    ids = []
    seen = set()
    for activity_ids in seat_index.values():
        for activity_id in activity_ids:
            if activity_id and activity_id not in seen:
                seen.add(activity_id)
                ids.append(activity_id)
    return ids
