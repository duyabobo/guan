#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from service.common.presence import idle_passport_ids, locations_of, remember_location
from service.common.profile_catalog import SCOPE_INFO, SCOPE_REQUIREMENT
from service.common.reactivate_due import ReactivateViewer, drop_cooled, pick_reactivate_jobs
from util.const.identity import RUNTIME_UNION_KEY, RUNTIME_UNION_TTL_SEC
from util.const.match import (
    MODEL_ACTIVITY_STATE_INVITING,
    MODEL_SEX_FEMALE_INDEX,
    MODEL_SEX_MALE_INDEX,
)
from util.const.notice import (
    HOME_PAGE,
    NOTICE_TEXT,
    REACTIVATE_IDLE,
    SCENE_REACTIVATE,
    THING_MAX_LEN,
)
from util.redis_conn import redisConn

_NEAR_LAT = 40.010
_NEAR_LNG = 116.340
_PLACE_LAT = 40.003
_PLACE_LNG = 116.339
_FAR_LAT = 31.230
_FAR_LNG = 121.470


class _Attr(object):
    def __init__(self, scope, dim_key, value_min=0, value_max=0, value_text=''):
        self.scope = scope
        self.dim_key = dim_key
        self.value_min = value_min
        self.value_max = value_max
        self.value_text = value_text


class _Activity(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.state = kwargs.get('state', MODEL_ACTIVITY_STATE_INVITING)
        self.start_time = kwargs.get('start_time')
        self.boy_passport_id = kwargs.get('boy_passport_id', 7)
        self.girl_passport_id = kwargs.get('girl_passport_id', 0)
        self.address_id = kwargs.get('address_id', 8)
        self.seat_locked = kwargs.get('seat_locked', False)


class _Address(object):
    def __init__(self):
        self.latitude = _PLACE_LAT
        self.longitude = _PLACE_LNG


def _info(sex, year=1995, home='北京'):
    return {
        'sex': _Attr(SCOPE_INFO, 'sex', value_min=sex),
        'birth_year': _Attr(SCOPE_INFO, 'birth_year', value_min=year),
        'height': _Attr(SCOPE_INFO, 'height', value_min=170),
        'weight': _Attr(SCOPE_INFO, 'weight', value_min=55),
        'home_region': _Attr(SCOPE_INFO, 'home_region', value_text=home),
    }


def _viewer(passport_id=9, sex=MODEL_SEX_FEMALE_INDEX, latitude=_NEAR_LAT, longitude=_NEAR_LNG, info=None):
    return ReactivateViewer(passport_id, latitude, longitude, info if info is not None else _info(sex))


def _pick(viewer, activity, profiles, now):
    return pick_reactivate_jobs([viewer], [activity], profiles, {activity.address_id: _Address()}, now)


def test_reactivate_copy_fits_wechat_thing():
    title, note = NOTICE_TEXT[SCENE_REACTIVATE]
    assert title == '有适合的人在等'
    assert note == '去选时间和地点见面'
    assert len(title) <= THING_MAX_LEN
    assert len(note) <= THING_MAX_LEN


def test_nearby_idle_match_gets_one_home_notice():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    now = start - datetime.timedelta(minutes=30)
    activity = _Activity(id=4, start_time=start)
    profiles = {7: {'info': _info(MODEL_SEX_MALE_INDEX), 'requirement': {}}}
    jobs = _pick(_viewer(), activity, profiles, now)
    assert len(jobs) == 1
    assert jobs[0].passport_id == 9
    assert jobs[0].scene == SCENE_REACTIVATE
    assert jobs[0].activity_id == 4
    assert jobs[0].start_time == start
    assert jobs[0].page == HOME_PAGE


def test_same_sex_seat_is_not_a_match():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    activity = _Activity(start_time=start, boy_passport_id=7)
    profiles = {7: {'requirement': {}}}
    viewer = _viewer(sex=MODEL_SEX_MALE_INDEX)
    assert _pick(viewer, activity, profiles, start - datetime.timedelta(minutes=30)) == []


def test_incomplete_profile_is_not_pushed():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    info = _info(MODEL_SEX_FEMALE_INDEX)
    del info['home_region']
    activity = _Activity(start_time=start)
    profiles = {7: {'requirement': {}}}
    viewer = _viewer(info=info)
    assert _pick(viewer, activity, profiles, start - datetime.timedelta(minutes=30)) == []


def test_requirement_miss_is_not_a_match():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    activity = _Activity(start_time=start)
    profiles = {7: {'requirement': {
        'birth_year': _Attr(SCOPE_REQUIREMENT, 'birth_year', value_min=1998, value_max=2000),
    }}}
    viewer = _viewer(info=_info(MODEL_SEX_FEMALE_INDEX, year=1990))
    assert _pick(viewer, activity, profiles, start - datetime.timedelta(minutes=30)) == []


def test_slot_outside_the_list_window_is_skipped():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    activity = _Activity(start_time=start)
    profiles = {7: {'requirement': {}}}
    too_early = start - datetime.timedelta(hours=3)
    assert _pick(_viewer(), activity, profiles, too_early) == []


def test_far_user_is_not_pushed():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    activity = _Activity(start_time=start)
    profiles = {7: {'requirement': {}}}
    viewer = _viewer(latitude=_FAR_LAT, longitude=_FAR_LNG)
    assert _pick(viewer, activity, profiles, start - datetime.timedelta(minutes=30)) == []


def test_inviter_and_locked_seat_are_skipped():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    now = start - datetime.timedelta(minutes=30)
    profiles = {7: {'requirement': {}}}
    own = _Activity(id=2, start_time=start, boy_passport_id=9, girl_passport_id=0)
    assert _pick(_viewer(passport_id=9, sex=MODEL_SEX_FEMALE_INDEX), own, profiles, now) == []
    locked = _Activity(id=3, start_time=start, seat_locked=True)
    assert _pick(_viewer(), locked, profiles, now) == []


def test_soonest_visible_slot_wins():
    now = datetime.datetime(2026, 10, 25, 10, 0, 0)
    sooner = _Activity(id=1, start_time=now + datetime.timedelta(minutes=20))
    later = _Activity(id=2, start_time=now + datetime.timedelta(minutes=40))
    profiles = {7: {'requirement': {}}}
    address_of = {sooner.address_id: _Address()}
    jobs = pick_reactivate_jobs([_viewer()], [later, sooner], profiles, address_of, now)
    assert [job.activity_id for job in jobs] == [1]


def test_recently_pushed_user_is_cooled():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    activity = _Activity(start_time=start)
    profiles = {7: {'requirement': {}}}
    jobs = _pick(_viewer(), activity, profiles, start - datetime.timedelta(minutes=30))
    assert drop_cooled(jobs, [9]) == []
    assert len(drop_cooled(jobs, [])) == 1


def test_runtime_key_age_marks_idle_users():
    fresh = RUNTIME_UNION_TTL_SEC
    quiet = int(RUNTIME_UNION_TTL_SEC - REACTIVATE_IDLE.total_seconds() - 60)
    redisConn.set(RUNTIME_UNION_KEY % 5, 'fresh', ex=fresh)
    redisConn.set(RUNTIME_UNION_KEY % 6, 'quiet', ex=quiet)
    assert idle_passport_ids([5, 6, 7]) == [6]


def test_list_location_roundtrip():
    remember_location(8, _NEAR_LAT, _NEAR_LNG)
    assert locations_of([8])[8] == (_NEAR_LAT, _NEAR_LNG)
    remember_location(9, 120, 20)
    assert 9 not in locations_of([9])
