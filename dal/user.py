#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from models import User

from util.const import USER_STATUS_CANCELLATION


def add_user_info_by_openid(db_session, openid):
    """
    加入一个微信注册的用户
    :param db_session:
    :param openid:
    :return:
    """
    user = User(
        openid=openid,
        mobile='',
        password='',
    )
    db_session.add(user)
    db_session.flush()
    return user


def get_user_info_by_openid(db_session, openid):
    """
    查询 user
    :param db_session:
    :param openid:
    :return:
    """
    return db_session.query(User). \
        filter(
        User.openid == openid,
        User.user_status < USER_STATUS_CANCELLATION
    ).first()
