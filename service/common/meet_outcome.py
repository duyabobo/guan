#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""见面结果：到期自动双方合适，一方合适只记自己，不合适同步双方。"""
import logging

from model.activity import ActivityModel
from util.const.base import MODEL_MEET_RESULT_FIT_CHOICE
from util.const.progress import meet_auto_fit_due, next_results_after_my_fit

logger = logging.getLogger(__name__)


def settle_due_meets(passport_id):
    """满 7 天仍未表态的约见面，写成双方合适。一次查出再一次更新。"""
    if not passport_id:
        return
    rows = ActivityModel.listUnsetSuccess(passport_id)
    due_ids = [row.id for row in rows if meet_auto_fit_due(row)]
    if not due_ids:
        return
    ActivityModel.updateBothMeetResultsByIds(due_ids, MODEL_MEET_RESULT_FIT_CHOICE)
    logger.info("auto fit meets passport=%s activities=%s", passport_id, due_ids)


def record_my_fit(activity, actor_passport_id):
    """合适、恢复关系只写下自己。对方仍是不合适时先清掉，双方变成半实心。"""
    if actor_passport_id not in (activity.boy_passport_id, activity.girl_passport_id):
        logger.info("meet fit skipped activity=%s actor=%s 不是参与者", activity.id, actor_passport_id)
        return
    boy_result, girl_result = next_results_after_my_fit(
        activity.boy_meet_result, activity.girl_meet_result,
        actor_passport_id == activity.boy_passport_id,
    )
    ActivityModel.updateEachMeetResult(activity.id, boy_result, girl_result)
    logger.info(
        "meet fit recorded activity=%s actor=%s boy=%s girl=%s",
        activity.id, actor_passport_id, boy_result, girl_result,
    )


def apply_synced_result(activity, actor_passport_id, meet_result_value):
    """不合适、结束关系写成双方同一个结果。"""
    ActivityModel.updateBothMeetResults(activity.id, meet_result_value)
    partner_id = _partner_id(activity, actor_passport_id)
    logger.info(
        "meet result synced activity=%s actor=%s partner=%s value=%s",
        activity.id, actor_passport_id, partner_id, meet_result_value,
    )


def _partner_id(activity, actor_passport_id):
    if actor_passport_id == activity.boy_passport_id:
        return activity.girl_passport_id
    if actor_passport_id == activity.girl_passport_id:
        return activity.boy_passport_id
    return 0
