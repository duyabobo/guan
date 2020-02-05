#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from models import AnswerInfo


def add_answer_info(db_session, guan_id, guan_info_id, answer_key, answer_evaluation):
    """
    增加一个 guan_info 记录
    :param db_session:
    :param guan_id:
    :param guan_info_id:
    :param answer_key:
    :param answer_evaluation:
    :return:
    """
    guan_info = AnswerInfo(
        guan_id=guan_id,
        guan_info_id=guan_info_id,
        answer_key=answer_key,
        answer_evaluation=answer_evaluation
    )
    db_session.add(guan_info)
    db_session.flush()
    return guan_info


def get_answer_infoes(db_session, guan_info_id):
    """
    获取某个 guan_info 的答案列表
    :param db_session:
    :param guan_info_id:
    :return:
    """
    return db_session.query(AnswerInfo).\
        filter(AnswerInfo.guan_info_id == guan_info_id).\
        order_by(AnswerInfo.id).\
        all()


def get_answer_info(db_session, answer_info_id):
    """
    查询一个 answer_info
    :param db_session:
    :param answer_info_id:
    :return:
    """
    return db_session.query(AnswerInfo).\
        filter(AnswerInfo.id == answer_info_id).\
        first()


def get_answer_infoes_by_ids(db_session, answer_info_ids):
    """
    查询一批 answer_info
    :param db_session:
    :param answer_info_ids:
    :return:
    """
    return db_session.query(AnswerInfo).\
        filter(AnswerInfo.id.in_(answer_info_ids)).\
        order_by(AnswerInfo.id).\
        all()
