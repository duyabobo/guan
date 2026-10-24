#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""语音是见面流程的第一步。已经出现双心、半实心或实心时，不再接受录音。"""
import logging

from model.activity import ActivityModel
from util.const.progress import calc_activity_progress, voice_blocked_by_progress

logger = logging.getLogger(__name__)


def voice_entry_blocked(passport_id):
    if not passport_id:
        return False
    activities = ActivityModel.getUserAllActivities(passport_id)
    for activity in activities:
        progress = calc_activity_progress(passport_id, activity)
        if not voice_blocked_by_progress(progress):
            continue
        logger.info(
            "语音录入被见面进度拦住 passport=%s activity=%s progress=%s",
            passport_id, activity.id, progress,
        )
        return True
    return False
