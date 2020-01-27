#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from dal.guan_info import get_guan_infoes
from dal.answers import get_answers


def get_guan_info_dict(db_session, guan_id):
    step = 1
    guan_infoes = get_guan_infoes(db_session, guan_id)
    total_step = len(guan_infoes)
    question_dict = {index: guan_info.question for index, guan_info in enumerate(guan_infoes)}
    answer_dict = {}
    for index, guan_info in enumerate(guan_infoes):
        answer_dict[index] = []
        answers = get_answers(db_session, guan_info.id)
        for answer in answers:
            answer_dict[index].append({
                'answer_key': answer.answer_key,
                'answer_id': answer.id
            })
    return {
        'step': step,
        'total_step': total_step,
        'question_dict': question_dict,
        'answer_dict': answer_dict
    }
