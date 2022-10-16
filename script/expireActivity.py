#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 活动过期，清空匹配缓存，每天跑一遍
from model.activity import ActivityModel
from ral.activity import cleanByActivity

if __name__ == "__main__":
    activityIds = ActivityModel.getExpireActivityIdsIn7Days()
    activityIds = [a.id for a in activityIds]
    for activityId in activityIds:
        cleanByActivity(activityId)
