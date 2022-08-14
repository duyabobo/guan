#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 自动添加活动（v1版本）
# 1，筛选当前是否存在空闲活动，如果不存在就继续。
# 2，筛选是否有可用的见面地点，如果存在就继续。
# 3，判断上一个添加的活动时间是否在周末，是否在早上10点到下午16点之间，如果就时间加上半小时，如果不是就初始化下一个周末的早上十点。
# 4，添加下一个活动。
import datetime

from sqlalchemy.orm import sessionmaker
import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current_dir))
from model.activity import ActivityModel
from model.address import AddressModel


class ActivityAutoCreater(object):
    def hasFreeActivity(self):
        return bool(ActivityModel.getLastFreeActivity())

    def getAvaliableAddress(self):
        return AddressModel.getLastAddress()

    def getLastActivity(self):
        return ActivityModel.getLastActivity()

    def getNextTime(self):
        lastActivity = self.getLastActivity()
        if lastActivity and lastActivity.start_time.weekday() > 4 and lastActivity.start_time.hour < 17:  # 最新的活动是周末
            nextTime = lastActivity.start_time + datetime.timedelta(minutes=30)
        else:
            now = datetime.datetime.now()
            lastTime = max(now, lastActivity.start_time) if lastActivity else now
            targetTime = lastTime + datetime.timedelta(days={0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 1, 6: 6}.get(lastTime.weekday()))
            nextTime = datetime.datetime(year=targetTime.year, month=targetTime.month, day=targetTime.day, hour=10)
        return nextTime

    def createActivity(self):
        if self.hasFreeActivity():
            return
        address = self.getAvaliableAddress()
        if not address:
            return
        nextTime = self.getNextTime()
        ActivityModel.addOne(address.id, nextTime)
        return


if __name__ == '__main__':
    aac = ActivityAutoCreater()
    aac.createActivity()
