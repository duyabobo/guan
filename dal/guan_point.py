#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'
from models import GuanPoint


def add_guan_point(db_session, user_id, guan_id, guan_point):
    """
    写入一条记录
    :param db_session:
    :param user_id:
    :param guan_id:
    :param guan_point:
    :return:
    """
    guan_point = GuanPoint(
        user_id=user_id,
        guan_id=guan_id,
        guan_point=guan_point
    )
    db_session.add(guan_point)
    db_session.flush()
    return guan_point
