#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'
from sqlalchemy import func

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


def get_guan_points_by_uid(db_session, user_id):
    """
    查询一个人已经参与的关关纪录
    :param db_session:
    :param user_id:
    :return:
    """
    return db_session.query(GuanPoint).filter(GuanPoint.user_id == user_id).all()


def get_answers_data(db_session):
    """
    统计参与人数
    :param db_session:
    :return:
    """
    return db_session.query(GuanPoint.guan_id, func.count('*').label('c')).\
        group_by(GuanPoint.guan_id)
