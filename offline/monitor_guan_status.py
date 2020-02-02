#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/2/2'
# 监控线下见面类关关的状态，每隔十分钟跑一次
from datetime import datetime

from dal.guanguan import get_guanguan_of_offline_meeting
from dal.guanguan import update_guanguan_status
from dal.offline_meeting import get_offline_meetings_by_guan_ids
from util.const import GUANGUAN_STATUS_OFFLINE
from util.database import mysql_offline_session

if __name__ == '__main__':
    guanguans = get_guanguan_of_offline_meeting(mysql_offline_session)
    guan_ids = [guan.id for guan in guanguans]
    offline_meetings = get_offline_meetings_by_guan_ids(mysql_offline_session, guan_ids)
    offline_meeting_dict = {
        offline_meeting.guan_id: offline_meeting for offline_meeting in offline_meetings
    }
    for guan_id in offline_meeting_dict:
        offline_meeting = offline_meeting_dict[guan_id]
        if offline_meeting.time < datetime.now():
            update_guanguan_status(mysql_offline_session, guan_id, GUANGUAN_STATUS_OFFLINE)
