#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/28'
from models import GuanAnswer
from util.const import GUAN_INFO_ID_USER_INFO


def add_guan_answer(db_session, user_id, guan_id, guan_info_id, answer_info_id):
    """
    关关问答回答数据
    :param db_session:
    :param user_id:
    :param guan_id:
    :param guan_info_id:
    :param answer_info_id:
    :return:
    """
    guan_answer = GuanAnswer(
        user_id=user_id,
        guan_id=guan_id,
        guan_info_id=guan_info_id,
        answer_info_id=answer_info_id,
    )
    db_session.add(guan_answer)
    db_session.flush()
    return guan_answer


def update_guan_answer(db_session, guan_answer, answer_info_id):
    """
    用户重新回答
    :param db_session:
    :param guan_answer:
    :param answer_info_id:
    :return:
    """
    guan_answer.answer_info_id = answer_info_id
    db_session.flush()
    return guan_answer


def get_guan_answer(db_session, user_id, guan_info_id):
    """
    获取关关问答数据
    :param db_session:
    :param user_id:
    :param guan_info_id:
    :return:
    """
    return db_session.query(GuanAnswer).\
        filter(GuanAnswer.user_id == user_id).\
        filter(GuanAnswer.guan_info_id == guan_info_id).\
        first()


def get_guan_answers_by_answer_info_id(db_session, answer_info_id):
    """
    查询某个问题的回答数据
    :param db_session:
    :param answer_info_id:
    :return:
    """
    return db_session.query(GuanAnswer).filter(GuanAnswer.answer_info_id == answer_info_id).all()


def get_user_info_from_guan_answer(db_session, user_id):
    """
    查询一个用户的基本信息数据（guan_id=GUAN_INFO_ID_USER_INFO）
    :param db_session:
    :param user_id:
    :return:
    """
    guan_info_id = GUAN_INFO_ID_USER_INFO
    return get_guan_answer(db_session, user_id, guan_info_id)
