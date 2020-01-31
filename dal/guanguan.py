#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/19'
from models import GuanGuan
from util.const import GUANGUAN_STATUS_ONLINE


def get_guanguan(db_session, guan_id):
    """
    获取一条记录
    :param db_session:
    :param guan_id:
    :return:
    """
    return db_session.query(GuanGuan).\
        filter(GuanGuan.id == guan_id).first()


def get_guanguan_list(db_session):
    """
    获取关关列表
    :param db_session:
    :return:
    """
    return db_session.query(GuanGuan).\
        filter(GuanGuan.status == GUANGUAN_STATUS_ONLINE).\
        order_by(GuanGuan.guan_type_id).all()


def get_guanguan_by_guan_type(db_session, guan_type_id):
    """
    获取关关列表
    :param db_session:
    :param guan_type_id:
    :return:
    """
    return db_session.query(GuanGuan).\
        filter(GuanGuan.guan_type_id == guan_type_id).\
        all()
