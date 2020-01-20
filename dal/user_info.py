#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from datetime import datetime

from models import UserInfo


def add_user_info(db_session, user_id):
    """
    添加一个用户信息记录
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
    根据 user_id 查询用户信息
    :param db_session:
    :param user_id:
    :return:
    """
    return db_session.query(UserInfo).filter(UserInfo.user_id == user_id).first()


def update_user_info(
        db_session,
        user_info,
        sex=None,
        age=None,
        height=None,
        degree=None
):
    """
    更新用户基本信息
    :param db_session:
    :param user_info:
    :param sex:
    :param age:
    :param height:
    :param degree:
    :return:
    """
    if sex is not None:
        user_info.sex = int(sex)
    if age is not None:
        user_info.year_of_birth = datetime.now().year - age
    if height is not None:
        user_info.height = height
    if degree is not None:
        user_info.degree = degree
    db_session.flush()
