#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/2/3'
import urllib
from datetime import timedelta

import requests

import util.config
from dal.guan_point import get_guan_points_by_guan_id
from dal.offline_meeting import get_offline_meetings_for_push
from dal.user import get_user_by_user_id
from ral.offline_meeting import get_offline_meeting_noti
from ral.offline_meeting import set_offline_meeting_noti
from util.database import mysql_offline_session
from util.database import redis_offline_session

if __name__ == '__main__':
    get_access_token_url = util.config.get("weixin", "get_access_token_url")
    appid = util.config.get("weixin", "appid")
    secret = util.config.get("weixin", "secret")
    grant_type = util.config.get("weixin", "grant_type")
    subscribe_send_url = util.config.get("weixin", "subscribe_send_url")
    offline_meeting_noti_tid = util.config.get("weixin", "offline_meeting_noti_tid")

    url_params = urllib.urlencode(
        {
            'appid': appid,
            'secret': secret,
            'grant_type': grant_type
        }
    )
    url = get_access_token_url + url_params
    res = requests.get(url).json()
    access_token = res.get('access_token', '')  # 7200秒内有效

    offline_meetings = get_offline_meetings_for_push(mysql_offline_session)
    for offline_meeting in offline_meetings:  # 不会太多
        guan_id = offline_meeting.guan_id
        guan_points = get_guan_points_by_guan_id(mysql_offline_session, guan_id)
        for guan_point in guan_points:  # 对参与人员逐个发服务推送
            user_id = guan_point.user_id
            if get_offline_meeting_noti(redis_offline_session, user_id, guan_id):
                continue
            user = get_user_by_user_id(mysql_offline_session, user_id)
            url_params = urllib.urlencode(
                {
                    'template_id': offline_meeting_noti_tid,
                    'touser': user.openid,
                    'access_token': access_token,
                    'page': 'guan_info?guan_id=%s' % guan_id,
                    'data': {
                        'thing1': {
                            'value': '线下活动开始提醒'
                        },
                        'thing2': {
                            'value': offline_meeting.address
                        },
                        'date3': {
                            'value': offline_meeting.time
                        },
                        'data4': {
                            'value': offline_meeting.time + timedelta(hours=2)
                        }
                    }
                }
            )
            url = get_access_token_url + url_params
            res = requests.get(url).json()
            set_offline_meeting_noti(redis_offline_session, user_id, guan_id)
