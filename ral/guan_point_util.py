#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'
from dal.guan_point import get_answer_user_cnt
from dal.guan_point import get_answer_user_cnt_by_guan_id


def get_answer_user_cnt_dict_from_db(db_session):
    """
    从 db 重新统计参与人数数据
    :param db_session:
    :return:
    """
    answers_data = get_answer_user_cnt(db_session)
    return {
        d.guan_id: d.c for d in answers_data
    }


def get_answer_user_cnt_from_db(db_session, guan_id):
    """
    重新查询某一个关关的参与人数
    :param db_session:
    :param guan_id:
    :return:
    """
    answer_user_cnt_data = get_answer_user_cnt_by_guan_id(db_session, guan_id)
    return answer_user_cnt_data.c
