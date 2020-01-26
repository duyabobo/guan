#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/24'
# 测评结果放 redis，（原始数据还是放到db）
import json
from guan_evaluation_utils.user_info import USER_INFO_EVALUATIONS


GUAN_EVALUATION_RESULT_DICT = {  # 这里只是临时文件，以后要定时脚本异步计算出结果的
    0: USER_INFO_EVALUATIONS
}


def get_guan_evaluation_key(guan_type, user_id):
    """
    返回登录查询 evaluation 的 key
    :param guan_type:
    :param user_id:
    :return:
    """
    return 'guan_evaluation:guan_type:' + str(guan_type) + 'user_id:' + str(user_id)


def set_evaluation_result(redis, user_id, guan_type):
    """
    设置(更新)关关问答的测评结果，无法删减，这里其实以后是用作定时脚本的逻辑实现
    :param redis:
    :param user_id:
    :param guan_type:
    :return:
    """
    old_evaluation = GUAN_EVALUATION_RESULT_DICT.get(guan_type, [])  # todo: 这里从 db 计算的
    guan_evaluation_key = get_guan_evaluation_key(guan_type, user_id)
    new_evaluation = json.dumps(old_evaluation)
    return redis.set(guan_evaluation_key, new_evaluation)


def get_evaluation_result(redis, user_id, guan_type):
    """
    获取关关问答的测评结果
    :param redis:
    :param user_id:
    :param guan_type:
    :return:
    """
    guan_evaluation_key = get_guan_evaluation_key(guan_type, user_id)
    try:
        return json.loads(redis.get(guan_evaluation_key))
    except:
        return []
