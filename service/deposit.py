#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""定金：支付前的页面、签到，以及到点或取消时的结算。"""
import datetime
import logging

from model.activity import ActivityModel
from model.meet_checkin import MeetCheckinModel
from model.meet_deposit import MeetDepositPayoutModel, MeetDepositSettleModel
from model.meet_fee_order import MeetFeeOrderModel
from service.common.notice_due import NoticeJob
from service.meet_fee import MeetFeeService
from service.meet_notice import MeetNoticeService
from util.const.base import (
    GUAN_INFO_OP_TYPE_CHECKIN,
    GUAN_INFO_OP_TYPE_INVITE,
    GUAN_INFO_OP_TYPE_JOIN,
    GUAN_INFO_OP_TYPE_REDEPOSIT,
)
from util.const.deposit import (
    CHECKIN_HINT,
    DEPOSIT_YUAN,
    METERS_PER_KM,
    OUTCOME_AWARD,
    OUTCOME_FORFEIT,
    OUTCOME_REFUND,
    OUTCOME_SKIP,
    PHASE_BEFORE,
    PHASE_OPEN,
    REDEPOSIT_HINT,
    TAKEN_NOTE,
    award_winner,
    checkin_phase,
    deposit_banner,
    deposit_confirm_hint,
    pair_outcome,
    within_checkin_radius,
)
from util.const.match import MODEL_ACTIVITY_STATE_INVITE_SUCCESS, MODEL_ACTIVITY_STATE_INVITING
from util.const.notice import (
    SCAN_ACTIVITY_LIMIT,
    SCENE_CANCELLED,
    SCENE_DEPOSIT_BACK,
    SCENE_DEPOSIT_FORFEIT,
    SCENE_DEPOSIT_LOSE,
    SCENE_DEPOSIT_TAKE,
    SCENE_NO_SHOW,
)
from util.const.progress import (
    MEET_AUTO_FIT_WAIT,
    MEET_CHOICE_WAIT,
    PROGRESS_SELECTED,
    PROGRESS_WAIT_MEET,
    STYLE_MEET,
    _button,
    calc_distance_km,
)
from util.const.response import (
    RESP_CHECKIN_CLOSED,
    RESP_CHECKIN_EARLY,
    RESP_CHECKIN_FAR,
    RESP_CHECKIN_NO_LOCATION,
    RESP_CHECKIN_NO_PLACE,
    RESP_DEPOSIT_MISSING,
    RESP_JOIN_ACTIVITY_FAILED,
    checkin_ok_msg,
)
from util.slot_blind import activity_slot_key

logger = logging.getLogger(__name__)

_SEAT_PAY_OPS = (GUAN_INFO_OP_TYPE_INVITE, GUAN_INFO_OP_TYPE_JOIN)


class _Plan(object):
    def __init__(self):
        self.refund_ids = []
        self.forfeit_ids = []
        self.award = None
        self.settle = None
        self.notices = []


def holds(passport_id, activity_id):
    return _consumed(passport_id, activity_id) is not None


def present(buttons, activity, passport_id, progress, viewer, now=None):
    """详情页的定金说明，以及签到、补定金按钮。"""
    if viewer or not activity:
        return list(buttons or []), {'required': False, 'yuan': 0, 'text': ''}
    now = now or datetime.datetime.now()
    order = _consumed(passport_id, activity.id)
    checked = bool(order and MeetCheckinModel.has_order(passport_id, order.id))
    fee = {'required': True, 'yuan': DEPOSIT_YUAN, 'text': deposit_banner(checked)}
    front = []
    if _show_checkin(activity, passport_id, progress, order, checked, now):
        button = _button('签到', 'operate', STYLE_MEET, True, op_type=GUAN_INFO_OP_TYPE_CHECKIN, hint=CHECKIN_HINT)
        button['needLocation'] = True
        front.append(button)
    if _show_redeposit(activity, passport_id, progress, order):
        front.append(_button(
            '支付定金', 'operate', STYLE_MEET, True,
            op_type=GUAN_INFO_OP_TYPE_REDEPOSIT, hint=REDEPOSIT_HINT,
        ))
    return front + _annotate(buttons), fee


def check_in(activity, passport_id, latitude, longitude, place_latitude, place_longitude, now=None):
    now = now or datetime.datetime.now()
    if not _seated(activity, passport_id) or activity.state != MODEL_ACTIVITY_STATE_INVITE_SUCCESS:
        logger.info("签到被拒绝 activity=%s passport=%s", getattr(activity, 'id', 0), passport_id)
        return RESP_JOIN_ACTIVITY_FAILED
    order = _consumed(passport_id, activity.id)
    if not order:
        return RESP_DEPOSIT_MISSING
    if MeetCheckinModel.has_order(passport_id, order.id):
        return checkin_ok_msg()
    phase = checkin_phase(activity.start_time, now)
    if phase == PHASE_BEFORE:
        return RESP_CHECKIN_EARLY
    if phase != PHASE_OPEN:
        return RESP_CHECKIN_CLOSED
    reached = _at_place(activity.id, passport_id, latitude, longitude, place_latitude, place_longitude)
    if reached is not True:
        return reached
    MeetCheckinModel.add_once(passport_id, activity.id, order.id)
    return checkin_ok_msg()


def on_solo_cancel(passport_id, activity_id):
    order = _consumed(passport_id, activity_id)
    if not order:
        logger.info("撤回邀请时没有可退的定金 passport=%s activity=%s", passport_id, activity_id)
        return 0
    return order.id


def on_agreed_cancel(activity, canceller_id, partner_id):
    """已约上后取消。留下的人拿走两笔：自己的退回，取消方的记给留下的人。"""
    slot = activity_slot_key(activity.id)
    canceller_order = _consumed(canceller_id, activity.id)
    partner_order = _consumed(partner_id, activity.id) if partner_id else None
    _award_canceller(partner_id, canceller_order, slot, activity.id)
    low_id, high_id = _sorted_ids(canceller_order, partner_order)
    if slot and (canceller_order or partner_order):
        MeetDepositSettleModel.add_once(slot, low_id, high_id, OUTCOME_AWARD, partner_id or 0)
    refund_id = partner_order.id if partner_order else 0
    return refund_id, _cancel_notices(activity, canceller_id, partner_id)


def settle_due(now):
    deadline = now - MEET_CHOICE_WAIT
    earliest = now - MEET_AUTO_FIT_WAIT
    rows = ActivityModel.list_deposit_due(earliest, deadline, SCAN_ACTIVITY_LIMIT)
    plans = _plans(rows)
    _apply(plans)
    _log_pending()


def _plans(rows):
    if not rows:
        return []
    slots = {row.id: activity_slot_key(row.id) for row in rows}
    orders = MeetFeeOrderModel.list_settle_orders(list(slots.values()))
    grouped = _group_orders(orders)
    checked = MeetCheckinModel.checked_order_ids([order.id for order in orders])
    done = MeetDepositSettleModel.done_pairs(list(slots.values()))
    plans = []
    for row in rows:
        plan = _plan_row(row, slots.get(row.id, ''), grouped, checked, done)
        if plan:
            plans.append(plan)
    return plans


def _plan_row(row, slot, grouped, checked, done):
    if not slot:
        logger.error("定金未结算，盲索引为空 activity=%s", row.id)
        return None
    pair = _pair_orders(grouped.get(slot, []), row.boy_passport_id, row.girl_passport_id)
    if pair is None:
        return _skip_plan(slot, done, row.id)
    low, high = pair
    if (slot, low.id, high.id) in done:
        return None
    left_on_time = low.id in checked
    right_on_time = high.id in checked
    outcome = pair_outcome(left_on_time, right_on_time)
    plan = _Plan()
    winner_id = 0
    if outcome == OUTCOME_REFUND:
        plan.refund_ids = [low.id, high.id]
        plan.notices = [_job(low.passport_id, SCENE_DEPOSIT_BACK, row), _job(high.passport_id, SCENE_DEPOSIT_BACK, row)]
    elif outcome == OUTCOME_FORFEIT:
        plan.forfeit_ids = [low.id, high.id]
        plan.notices = [
            _job(low.passport_id, SCENE_DEPOSIT_FORFEIT, row),
            _job(high.passport_id, SCENE_DEPOSIT_FORFEIT, row),
        ]
    else:
        winner_id = award_winner(left_on_time, low.passport_id, high.passport_id)
        winner_order, loser_order = (low, high) if left_on_time else (high, low)
        plan.refund_ids = [winner_order.id]
        plan.award = (winner_id, loser_order, slot)
        plan.notices = [
            _job(winner_order.passport_id, SCENE_DEPOSIT_TAKE, row),
            _job(loser_order.passport_id, SCENE_DEPOSIT_LOSE, row),
        ]
    plan.settle = (slot, low.id, high.id, outcome, winner_id)
    logger.info("定金结算 activity=%s outcome=%s", row.id, outcome)
    return plan


def _skip_plan(slot, done, activity_id):
    if (slot, 0, 0) in done:
        return None
    logger.info("这场没有两笔定金，跳过结算 activity=%s", activity_id)
    plan = _Plan()
    plan.settle = (slot, 0, 0, OUTCOME_SKIP, 0)
    return plan


def _apply(plans):
    if not plans:
        return
    logger.info("待结算定金 %s 对", len(plans))
    refund_ids = []
    notices = []
    for plan in plans:
        _apply_money(plan)
        refund_ids.extend(plan.refund_ids)
        notices.extend(_filter_notices(plan.notices))
    for order_id in refund_ids:
        MeetFeeService.refund(order_id)
    for plan in plans:
        if plan.settle:
            MeetDepositSettleModel.add_once(*plan.settle)
    MeetNoticeService.dispatch(notices, record_sent=True)


def _apply_money(plan):
    for order_id in plan.forfeit_ids:
        MeetFeeOrderModel.mark_forfeit(order_id)
    if plan.award:
        winner_id, loser_order, slot = plan.award
        _award_order(winner_id, loser_order, slot)


def _award_canceller(partner_id, canceller_order, slot, activity_id):
    if not canceller_order:
        logger.info("取消方没有可扣的定金 activity=%s", activity_id)
        return
    if not partner_id:
        MeetFeeOrderModel.mark_forfeit(canceller_order.id)
        logger.info("取消时没有对方，定金不退 activity=%s", activity_id)
        return
    _award_order(partner_id, canceller_order, slot)


def _award_order(winner_id, loser_order, slot):
    if not MeetFeeOrderModel.mark_awarded(loser_order.id):
        return
    MeetDepositPayoutModel.add_once(winner_id, slot, loser_order.id, loser_order.amount_fen)


def _log_pending():
    pending = MeetDepositPayoutModel.count_pending()
    if pending:
        logger.info("待打给对方的定金 %s 笔，微信退款不能转给另一个人", pending)


def _at_place(activity_id, passport_id, latitude, longitude, place_latitude, place_longitude):
    if not place_latitude or not place_longitude:
        logger.info("签到被拒绝，地点没有坐标 activity=%s", activity_id)
        return RESP_CHECKIN_NO_PLACE
    if not latitude or not longitude:
        logger.info("签到被拒绝，没有定位 activity=%s passport=%s", activity_id, passport_id)
        return RESP_CHECKIN_NO_LOCATION
    distance_km = calc_distance_km(latitude, longitude, place_latitude, place_longitude)
    if not within_checkin_radius(distance_km):
        meters = None if distance_km is None else int(distance_km * METERS_PER_KM)
        logger.info("签到被拒绝，不在地点附近 activity=%s passport=%s meters=%s", activity_id, passport_id, meters)
        return RESP_CHECKIN_FAR
    return True


def _show_checkin(activity, passport_id, progress, order, checked, now):
    if progress != PROGRESS_WAIT_MEET or not order or checked:
        return False
    if not _seated(activity, passport_id):
        return False
    return checkin_phase(activity.start_time, now) == PHASE_OPEN


def _show_redeposit(activity, passport_id, progress, order):
    if progress != PROGRESS_SELECTED or order:
        return False
    return activity.state == MODEL_ACTIVITY_STATE_INVITING and _seated(activity, passport_id)


def _annotate(buttons):
    hint = deposit_confirm_hint()
    annotated = []
    for button in buttons or []:
        if button.get('opType') not in _SEAT_PAY_OPS:
            annotated.append(button)
            continue
        copied = dict(button)
        copied['needConfirm'] = True
        copied['hint'] = hint
        annotated.append(copied)
    return annotated


def _seated(activity, passport_id):
    if not activity or not passport_id:
        return False
    return passport_id in (activity.boy_passport_id or 0, activity.girl_passport_id or 0)


def _consumed(passport_id, activity_id):
    if not passport_id or not activity_id:
        return None
    return MeetFeeOrderModel.find_consumed(passport_id, activity_id)


def _pair_orders(orders, boy_id, girl_id):
    """只取当前两个座位上、各自最新的一笔。换人之后不把上一对算进来。"""
    seated = {boy_id or 0, girl_id or 0}
    seated.discard(0)
    if len(seated) != 2:
        return None
    latest = {}
    for order in orders or []:
        if order.passport_id not in seated:
            continue
        current = latest.get(order.passport_id)
        if current is None or order.id > current.id:
            latest[order.passport_id] = order
    if len(latest) != 2:
        return None
    chosen = list(latest.values())
    chosen.sort(key=lambda item: item.id)
    return chosen[0], chosen[1]


def _group_orders(orders):
    grouped = {}
    for order in orders or []:
        grouped.setdefault(order.slot_key, []).append(order)
    return grouped


def _sorted_ids(left, right):
    ids = sorted(order.id for order in (left, right) if order)
    if not ids:
        return 0, 0
    if len(ids) == 1:
        return ids[0], 0
    return ids[0], ids[1]


def _job(passport_id, scene, activity):
    if not passport_id or not activity or not activity.start_time:
        return None
    return NoticeJob(passport_id, scene, activity.id, activity.start_time)


def _cancel_notices(activity, canceller_id, partner_id):
    notices = []
    if partner_id:
        notices.append(NoticeJob(partner_id, SCENE_CANCELLED, activity.id, activity.start_time, TAKEN_NOTE))
    if canceller_id:
        notices.append(NoticeJob(canceller_id, SCENE_NO_SHOW, activity.id, activity.start_time))
    return [job for job in notices if job.start_time]


def _filter_notices(notices):
    return [job for job in notices if job]
