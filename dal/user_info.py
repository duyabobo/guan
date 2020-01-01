#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from models import UserInfo


def add_user_info(db_session, user_id):
    """
    添加一个男性用户信息记录
    :param db_session:
    :param user_id:
    :return:
    """
    user_info = UserInfo(user_id=user_id)
    db_session.add(user_info)
    db_session.flush()
    return user_info


def get_user_info_by_uid(db_session, user_id):
    """
    根据id查询用户信息
    :param db_session:
    :param user_id:
    :return:
    """
    return db_session.query(UserInfo).filter(UserInfo.user_id == user_id).first()
