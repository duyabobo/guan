#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'
from dal.guan_point import get_answers_data


def get_answers_dict_from_db(db_session):
    """
    从 db 重新统计参与人数数据
    :param db_session:
    :return:
    """
    answers_data = get_answers_data(db_session)
    return {
        d.guan_id: d.c for d in answers_data
    }
