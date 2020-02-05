#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/19'
from models import GuanGuan
from util.const import GUANGUAN_STATUS_ONLINE
from util.const import GUAN_TYPE_ID_MEET


def add_guanguan(db_session, name, guan_type_id, guan_point):
    """
    增加一个关关
    :param db_session:
    :param name:
    :param guan_type_id:
    :param guan_point:
    :return:
    """
    guanguan = GuanGuan(
        name=name,
        guan_type_id=guan_type_id,
        guan_point=guan_point
    )
    db_session.add(guanguan)
    db_session.flush()
    return guanguan


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
        filter(GuanGuan.guan_type_id == guan_type_id). \
        filter(GuanGuan.status == GUANGUAN_STATUS_ONLINE).\
        all()


def get_guanguan_of_offline_meeting(db_session):
    """
    获取线下见面类关关列表
    :param db_session:
    :return:
    """
    guan_type_id = GUAN_TYPE_ID_MEET
    return get_guanguan_by_guan_type(db_session, guan_type_id)


def update_guanguan_status(db_session, guan_id, status):
    """
    修改关关的 status
    :param db_session:
    :param guan_id:
    :param status:
    :return:
    """
    guanguan = get_guanguan(db_session, guan_id)
    guanguan.status = status
    db_session.flush()
    return guanguan
