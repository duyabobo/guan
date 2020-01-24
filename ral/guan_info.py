#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/20'
import json
from ral.guan_info_utils.user_info import USER_INFO_DICT

GUAN_INFO_DICT = {
    1: USER_INFO_DICT
}


def get_guan_info_key(guan_id):
    """
    返回登录查询 redis 的 key
    :param guan_id:
    :return:
    """
    return 'guan_id:' + str(guan_id)


def get_guan_info(redis, guan_id):
    """
    获取 guan_info
    :param redis:
    :param guan_id:
    :return:
    """
    guan_info_key = get_guan_info_key(guan_id)
    try:
        return json.loads(redis.get(guan_info_key))
    except:
        return {}


def set_guan_info(redis, guan_id):
    """
    存储 guan_info
    :param redis:
    :param guan_id:
    :return:
    """
    guan_info_key = get_guan_info_key(guan_id)
    if guan_id not in GUAN_INFO_DICT:
        return -1
    guan_info = GUAN_INFO_DICT[guan_id]
    try:
        return redis.set(guan_info_key, json.dumps(guan_info))
    except:
        return -1
