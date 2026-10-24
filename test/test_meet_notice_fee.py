#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from service.common.notice_due import NoticeJob, drop_sent, scheduled_notices, sent_key
from util.const.match import MODEL_ACTIVITY_STATE_INVITE_SUCCESS, MODEL_ACTIVITY_STATE_INVITING
from util.const.deposit import (
    DEPOSIT_YUAN,
    OUTCOME_AWARD,
    OUTCOME_FORFEIT,
    OUTCOME_REFUND,
    PHASE_BEFORE,
    PHASE_CLOSED,
    PHASE_OPEN,
    award_winner,
    CHECKIN_RADIUS_METERS,
    checkin_phase,
    deposit_fen,
    pair_outcome,
    within_checkin_radius,
)
from util.const.meet_fee import (
    FEN_PER_YUAN,
    format_out_refund_no,
    format_out_trade_no,
    quit_records_no_show,
)
from util.const.notice import (
    LIST_EXPIRE_LEAD,
    MEET_SOON_LEAD,
    SCENE_DECIDE,
    SCENE_LIST_EXPIRE,
    SCENE_MEET_SOON,
    THING_MAX_LEN,
    boss_greeting,
    clip_thing,
)
from util.const.progress import MEET_AUTO_FIT_WAIT, MEET_CHOICE_WAIT, calc_distance_km
from util.wx_pay import client_pay_params, sign_v2


class _Activity(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 1)
        self.state = kwargs.get('state', 0)
        self.start_time = kwargs.get('start_time')
        self.boy_passport_id = kwargs.get('boy_passport_id', 0)
        self.girl_passport_id = kwargs.get('girl_passport_id', 0)
        self.boy_meet_result = kwargs.get('boy_meet_result', 0)
        self.girl_meet_result = kwargs.get('girl_meet_result', 0)


def test_deposit_is_flat_and_checkin_allows_one_hour_late():
    assert deposit_fen() == DEPOSIT_YUAN * FEN_PER_YUAN
    start = datetime.datetime(2026, 10, 25, 10, 0, 0)
    assert checkin_phase(start, start - datetime.timedelta(minutes=1)) == PHASE_BEFORE
    assert checkin_phase(start, start) == PHASE_OPEN
    assert checkin_phase(start, start + datetime.timedelta(minutes=60)) == PHASE_CLOSED
    assert checkin_phase(start, start + datetime.timedelta(minutes=59)) == PHASE_OPEN
    assert pair_outcome(True, True) == OUTCOME_REFUND
    assert pair_outcome(True, False) == OUTCOME_AWARD
    assert pair_outcome(False, False) == OUTCOME_FORFEIT
    assert award_winner(True, 3, 4) == 3
    assert award_winner(False, 3, 4) == 4
    near = calc_distance_km(39.9000, 116.4000, 39.9010, 116.4000)
    far = calc_distance_km(39.9000, 116.4000, 39.9100, 116.4000)
    assert near is not None and near * 1000 <= CHECKIN_RADIUS_METERS
    assert within_checkin_radius(near) is True
    assert within_checkin_radius(far) is False
    assert within_checkin_radius(None) is False


def test_only_quit_after_agreed_is_no_show():
    assert quit_records_no_show(MODEL_ACTIVITY_STATE_INVITE_SUCCESS, MODEL_ACTIVITY_STATE_INVITE_SUCCESS) is True
    assert quit_records_no_show(MODEL_ACTIVITY_STATE_INVITING, MODEL_ACTIVITY_STATE_INVITE_SUCCESS) is False


def test_trade_no_fits_wechat_limit():
    trade_no = format_out_trade_no(12)
    refund_no = format_out_refund_no(12)
    assert trade_no.startswith('MF')
    assert refund_no.startswith('MR')
    assert len(trade_no) <= 32
    assert trade_no != refund_no


def test_pay_sign_ignores_empty_and_sign_field():
    params = {'appid': 'wx1', 'mch_id': '100', 'total_fee': 1000, 'body': '', 'sign': 'OLD'}
    signed = sign_v2(params, 'secret')
    assert signed == sign_v2({'mch_id': '100', 'total_fee': 1000, 'appid': 'wx1'}, 'secret')
    assert signed != sign_v2({'appid': 'wx1', 'mch_id': '100', 'total_fee': 1}, 'secret')
    assert len(signed) == 32
    assert signed == signed.upper()


def test_client_pay_params_are_signed():
    params = client_pay_params('prepay', 'wx1', 'secret', 100, 'nonce')
    assert params['package'] == 'prepay_id=prepay'
    assert len(params['paySign']) == 32
    assert params['signType'] == 'MD5'


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
