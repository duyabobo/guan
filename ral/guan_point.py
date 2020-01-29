#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'
from guan_point_util import get_answers_dict_from_db


def get_guan_point_answers_key():
    """
    返回登录查询 redis 的 key
    :return:
    """
    return 'guan_point:answers'


def get_answers_dict(redis, db_session):
    """
    获取问答参与人数字典数据
    :param redis:
    :param db_session:
    :return: {guan_id: answer_cnt, ...}
    """
    key = get_guan_point_answers_key()
    answers_dict = redis.hgetall(key)
    if not answers_dict:
        answers_dict = get_answers_dict_from_db(db_session)
        redis.hmset(key, answers_dict)
    return answers_dict


def get_answers(redis, guan_id):
    """
    获取参与人数
    :param redis:
    :param guan_id:
    :return:
    """
    key = get_guan_point_answers_key()
    return redis.hget(key, guan_id)


def incr_answers(redis, guan_id):
    """
    增加关关的参与人数
    :param redis:
    :param guan_id:
    :return:
    """
    key = get_guan_point_answers_key()
    answers = get_answers(redis, guan_id)
    answers = int(answers) if answers else 0
    return redis.hset(key, guan_id, answers + 1)
