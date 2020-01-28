#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/19'
from models import GuanGuan


def get_guanguan_list(db_session):
    """
    获取关关列表
    :param db_session:
    :return:
    """
    return db_session.query(GuanGuan).all()


def get_guanguan_by_guan_type(db_session, guan_type):
    """
    获取关关列表
    :param db_session:
    :param guan_type:
    :return:
    """
    return db_session.query(GuanGuan).\
        filter(GuanGuan.guan_type == guan_type).\
        all()
