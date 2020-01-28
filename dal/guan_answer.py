#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/28'
from models import GuanAnswer


def add_guan_answer(db_session, user_id, answer_id):
    """
    关关问答回答数据
    :param db_session:
    :param user_id:
    :param answer_id:
    :return:
    """
    guan_answer = GuanAnswer(
        user_id=user_id,
        answer_id=answer_id,
    )
    db_session.add(guan_answer)
    db_session.flush()
    return guan_answer
