#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from service.common.notice_due import NoticeJob, drop_sent, scheduled_notices, sent_key
from util.const.match import MODEL_ACTIVITY_STATE_INVITE_SUCCESS, MODEL_ACTIVITY_STATE_INVITING
from util.const.notice import (
    LIST_EXPIRE_LEAD,
    MEET_ARRIVE_WINDOW,
    MEET_SOON_LEAD,
    SCENE_DECIDE,
    SCENE_LIST_EXPIRE,
    SCENE_MEET_ARRIVE,
    SCENE_MEET_SOON,
    SMS_REQUIRED_SCENES,
    THING_MAX_LEN,
    boss_greeting,
    clip_thing,
)
from util.const.progress import MEET_AUTO_FIT_WAIT, MEET_CHOICE_WAIT


class _Activity(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.state = kwargs.get('state', 0)
        self.start_time = kwargs.get('start_time')
        self.boy_passport_id = kwargs.get('boy_passport_id', 0)
        self.girl_passport_id = kwargs.get('girl_passport_id', 0)
        self.boy_meet_result = kwargs.get('boy_meet_result', 0)
        self.girl_meet_result = kwargs.get('girl_meet_result', 0)


def test_meet_push_tells_them_what_to_say_to_the_owner():
    ten = datetime.datetime(2026, 10, 25, 10, 0, 0)
    half = datetime.datetime(2026, 10, 25, 10, 30, 0)
    late = datetime.datetime(2026, 10, 25, 23, 59, 0)
    assert boss_greeting(ten) == '你好老板，我十点约了人'
    assert boss_greeting(half) == '你好老板，我十点半约了人'
    assert boss_greeting(late) == '你好老板，我二十三点五十九分约了人'
    assert len(boss_greeting(late)) <= THING_MAX_LEN


def test_thing_is_clipped_to_wechat_limit():
    assert clip_thing('见面') == '见面'
    assert len(clip_thing('场' * (THING_MAX_LEN + 5))) == THING_MAX_LEN


def test_list_expire_only_for_inviter_in_last_fifteen_minutes():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    inviting = _Activity(
        state=MODEL_ACTIVITY_STATE_INVITING,
        start_time=start,
        boy_passport_id=7,
    )
    inside = scheduled_notices(inviting, start - LIST_EXPIRE_LEAD)
    assert [job.scene for job in inside] == [SCENE_LIST_EXPIRE]
    assert inside[0].passport_id == 7
    too_early = scheduled_notices(inviting, start - LIST_EXPIRE_LEAD - datetime.timedelta(minutes=1))
    assert too_early == []
    assert scheduled_notices(inviting, start) == []


def test_meet_soon_goes_to_both_within_one_hour():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    agreed = _Activity(
        state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
        start_time=start,
        boy_passport_id=3,
        girl_passport_id=4,
    )
    jobs = scheduled_notices(agreed, start - MEET_SOON_LEAD)
    assert {job.passport_id for job in jobs} == {3, 4}
    assert {job.scene for job in jobs} == {SCENE_MEET_SOON}
    assert scheduled_notices(agreed, start - MEET_SOON_LEAD - datetime.timedelta(minutes=1)) == []
    assert SCENE_MEET_SOON in SMS_REQUIRED_SCENES


def test_meet_arrive_covers_the_first_quarter_hour():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    agreed = _Activity(
        state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
        start_time=start,
        boy_passport_id=3,
        girl_passport_id=4,
    )
    jobs = scheduled_notices(agreed, start)
    assert {job.scene for job in jobs} == {SCENE_MEET_ARRIVE}
    assert {job.passport_id for job in jobs} == {3, 4}
    assert scheduled_notices(agreed, start - datetime.timedelta(seconds=1)) != []
    assert SCENE_MEET_ARRIVE not in {job.scene for job in scheduled_notices(agreed, start - datetime.timedelta(seconds=1))}
    assert scheduled_notices(agreed, start + MEET_ARRIVE_WINDOW) != []
    assert scheduled_notices(agreed, start + MEET_ARRIVE_WINDOW + datetime.timedelta(seconds=1)) == []
    assert SCENE_MEET_ARRIVE in SMS_REQUIRED_SCENES


def test_decide_opens_one_hour_after_start_and_stops_at_seven_days():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    agreed = _Activity(
        state=MODEL_ACTIVITY_STATE_INVITE_SUCCESS,
        start_time=start,
        boy_passport_id=3,
        girl_passport_id=4,
    )
    ready = scheduled_notices(agreed, start + MEET_CHOICE_WAIT)
    assert {job.scene for job in ready} == {SCENE_DECIDE}
    assert scheduled_notices(agreed, start + MEET_CHOICE_WAIT - datetime.timedelta(minutes=1)) == []
    assert scheduled_notices(agreed, start + MEET_AUTO_FIT_WAIT) == []


def test_drop_sent_keeps_unsent_scene():
    start = datetime.datetime(2026, 10, 25, 11, 0, 0)
    jobs = [
        NoticeJob(3, SCENE_DECIDE, 9, start),
        NoticeJob(4, SCENE_DECIDE, 9, start),
    ]
    kept = drop_sent(jobs, {sent_key(9, 3, SCENE_DECIDE)})
    assert [job.passport_id for job in kept] == [4]
