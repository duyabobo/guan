#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from models import Answers


def get_answers(db_session, guan_info_id):
    """
    获取某个 guan_info 的答案列表
    :param db_session:
    :param guan_info_id:
    :return:
    """
    return db_session.query(Answers).\
        filter(Answers.guan_info_id == guan_info_id).\
        order_by(Answers.id).\
        all()
