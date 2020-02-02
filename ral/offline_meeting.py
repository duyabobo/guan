#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/2/3'


def get_offline_meeting_key(user_id, guan_id):
    """
    返回登录查询 redis 的 key
    :param user_id:
    :param guan_id:
    :return:
    """
    return 'offline_meeting:user_id:%s:guan_id:%s' % (user_id, guan_id)


def get_offline_meeting_noti(redis, user_id, guan_id):
    """
    获取缓存记录
    :param redis:
    :param user_id:
    :param guan_id:
    :return:
    """
    key = get_offline_meeting_key(user_id, guan_id)
    return redis.get(key)


def set_offline_meeting_noti(redis, user_id, guan_id):
    """
    计入缓存
    :param redis:
    :param user_id:
    :param guan_id:
    :return:
    """
    key = get_offline_meeting_key(user_id, guan_id)
    return redis.set(key, 1, ex=24*3600)
