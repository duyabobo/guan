#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/20'
import json

from guan_info_util import get_guan_info_dict


def get_guan_info_key(guan_id):
    """
    返回登录查询 redis 的 key
    :param guan_id:
    :return:
    """
    return 'guan_id:' + str(guan_id)


def get_guan_info(redis, db_session, guan_id):
    """
    获取 guan_info，先读 redis，每次读都要到 db 去算，并把计算结果覆盖 redis
    :param redis:
    :param db_session:
    :param guan_id:
    :return:
    """
    guan_info_key = get_guan_info_key(guan_id)
    guan_info_dict = {}
    try:
        guan_info_dict = json.loads(redis.get(guan_info_key))
    finally:
        if not guan_info_dict:
            guan_info_dict = get_guan_info_dict(db_session, guan_id)
            set_guan_info(redis, guan_id, guan_info_dict)
    return guan_info_dict


def set_guan_info(redis, guan_id, guan_info_dict):
    """
    存储 guan_info
    :param redis:
    :param guan_id:
    :param guan_info_dict: json
    :return:
    """
    guan_info_key = get_guan_info_key(guan_id)
    try:
        return redis.set(guan_info_key, json.dumps(guan_info_dict))
    finally:
        return -1
