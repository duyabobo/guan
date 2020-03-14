#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/24'
# 测评结果放 redis，（原始数据还是放到db）
import json

from guan_evaluation_util import get_evaluation_result_list


def get_guan_evaluation_key(guan_type, user_id):
    """
    返回登录查询 evaluation 的 key
    :param guan_type:
    :param user_id:
    :return:
    """
    return 'guan_evaluation:guan_type:' + str(guan_type) + 'user_id:' + str(user_id)


def set_evaluation_result(redis, user_id, guan_type, evaluation_result):
    """
    设置(更新)关关问答的测评结果
    :param redis:
    :param user_id:
    :param guan_type:
    :param evaluation_result:
    :return:
    """
    guan_evaluation_key = get_guan_evaluation_key(guan_type, user_id)
    evaluation_result = json.dumps(evaluation_result)
    return redis.set(guan_evaluation_key, evaluation_result)


def get_evaluation_result(redis, db_session, user_id, guan_type_id):
    """
    获取关关问答的测评结果
    :param redis:
    :param db_session:
    :param user_id:
    :param guan_type_id:
    :return:
    """
    guan_evaluation_key = get_guan_evaluation_key(guan_type_id, user_id)
    try:
        evaluation_result = json.loads(redis.get(guan_evaluation_key))
    except TypeError:
        evaluation_result = get_evaluation_result_list(db_session, user_id, guan_type_id)
        set_evaluation_result(redis, user_id, guan_type_id, evaluation_result)
    return evaluation_result
