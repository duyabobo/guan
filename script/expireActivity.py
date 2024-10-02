#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 活动过期，清空匹配缓存，每天跑一遍
import os
import sys
from datetime import datetime

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))

from model.activity import ActivityModel
from ral.activity import cleanByActivity
from util.const.match import MODEL_ACTIVITY_STATE_EMPTY


if __name__ == "__main__":
    activityIds = ActivityModel.getExpireActivityIds()
    activityIds = [a.id for a in activityIds]
    for activityId in activityIds:
        activity = ActivityModel.getById(activityId)
        if not activity:
            continue
        if activity.state != MODEL_ACTIVITY_STATE_EMPTY and activity.start_time > datetime.now():
            continue
        cleanByActivity(activityId)
