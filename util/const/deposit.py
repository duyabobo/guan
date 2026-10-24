#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""见面定金。双方各付一笔，按时签到原路退回。"""

from util.const.meet_fee import FEN_PER_YUAN
from util.const.progress import MEET_CHOICE_WAIT

DEPOSIT_YUAN = 10
CHECKIN_RADIUS_METERS = 200
METERS_PER_KM = 1000

PHASE_BEFORE = 'before'
PHASE_OPEN = 'open'
PHASE_CLOSED = 'closed'

OUTCOME_REFUND = 'refund'
OUTCOME_AWARD = 'award'
OUTCOME_FORFEIT = 'forfeit'
OUTCOME_SKIP = 'skip'

PAYOUT_PENDING = 0

CHECKIN_HINT = '到店后用定位签到。开始后1小时内，且离地点200米内，才算按时'
REDEPOSIT_HINT = '继续等下一位之前，需要重新支付定金'
TAKEN_NOTE = '双方定金归你'
LOSE_NOTE = '双方定金归对方'


def deposit_fen():
    return DEPOSIT_YUAN * FEN_PER_YUAN


def deposit_banner(checked_in):
    if checked_in:
        return '已签到。双方都在开始后1小时内签到，定金原路退回'
    return '见面定金%d元。开始后1小时内签到则退回；爽约或超时未到，定金归对方' % DEPOSIT_YUAN


def deposit_confirm_hint():
    return '需支付%d元定金。按时签到后退回；爽约或超时未到，定金归对方' % DEPOSIT_YUAN


def within_checkin_radius(distance_km):
    """人必须在地点 200 米内。没有算出距离就不当作到店。"""
    if distance_km is None:
        return False
    return distance_km * METERS_PER_KM <= CHECKIN_RADIUS_METERS


def checkin_phase(start, now, grace=None):
    """开始前不能签。开始后 1 小时内算按时，含这 1 小时里的迟到。"""
    grace = MEET_CHOICE_WAIT if grace is None else grace
    if not start or not now:
        return PHASE_CLOSED
    if now < start:
        return PHASE_BEFORE
    if now >= start + grace:
        return PHASE_CLOSED
    return PHASE_OPEN


def pair_outcome(left_on_time, right_on_time):
    """两人都按时则退回。只有一人按时，这一人拿走两笔。两人都不按时，两笔都不归任何人。"""
    if left_on_time and right_on_time:
        return OUTCOME_REFUND
    if left_on_time or right_on_time:
        return OUTCOME_AWARD
    return OUTCOME_FORFEIT


def award_winner(left_on_time, left_id, right_id):
    if left_on_time:
        return left_id
    return right_id
