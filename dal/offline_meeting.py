#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/2/1'
from datetime import datetime
from datetime import timedelta
from models import OfflineMeeting


def get_offline_meetings_by_guan_ids(db_session, all_guan_ids):
    """
    查询线下活动数据
    :param db_session:
    :param all_guan_ids:
    :return:
    """
    return db_session.query(OfflineMeeting).\
        filter(OfflineMeeting.guan_id.in_(all_guan_ids)).all()


def get_offline_meeting_by_guan_id(db_session, guan_id):
    """
    查询一个活动数据
    :param db_session:
    :param guan_id:
    :return:
    """
    return db_session.query(OfflineMeeting).\
        filter(OfflineMeeting.guan_id == guan_id).first()


def get_offline_meetings_for_push(db_session):
    """
    获取推送的目标数据
    :param db_session:
    :return:
    """
    now = datetime.now()
    return db_session.query(OfflineMeeting).\
        filter(OfflineMeeting.time > now - timedelta(days=1)).\
        filter(OfflineMeeting.time < now).\
        all()
