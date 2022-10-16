#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 活动过期，清空匹配缓存，每天跑一遍
import os
import sys

from model.activity import ActivityModel
from ral.activity import cleanByActivity

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))


if __name__ == "__main__":
    activityIds = ActivityModel.getExpireActivityIdsIn7Days()
    activityIds = [a.id for a in activityIds]
    for activityId in activityIds:
        cleanByActivity(activityId)
