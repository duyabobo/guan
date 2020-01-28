#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from dal.answer_info import get_answer_infoes
from dal.guan_info import get_guan_infoes


def get_guan_info_dict(db_session, guan_id):
    """
    从 db 计算 guan_info
    :param db_session:
    :param guan_id:
    :return:
    """
    step = 0  # todo 这里以后不一定每次都是0
    guan_infoes = get_guan_infoes(db_session, guan_id)
    total_step = len(guan_infoes) - 1
    question_dict = {index: guan_info.question for index, guan_info in enumerate(guan_infoes)}
    answer_dict = {}
    for index, guan_info in enumerate(guan_infoes):
        answer_dict[index] = []
        answer_infoes = get_answer_infoes(db_session, guan_info.id)
        for answer_info in answer_infoes:
            answer_dict[index].append({
                'answer_key': answer_info.answer_key,
                'answer_info_id': answer_info.id
            })
    return {
        'step': step,
        'total_step': total_step,
        'question_dict': question_dict,
        'answer_dict': answer_dict
    }
