#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'
from dal.answer_info import get_answer_infoes_by_ids
from dal.guan_answer import get_guan_answer
from dal.guan_info import get_guan_infoes
from dal.guanguan import get_guanguan_by_guan_type
from util.const import GUAN_TYPE_ID_MEET


def get_evaluation_result_list(db_session, user_id, guan_type_id):
    guanguan = get_guanguan_by_guan_type(db_session, guan_type_id)
    guan_ids = [guan.id for guan in guanguan]
    guan_infoes = []
    for guan_id in guan_ids:
        guan_infoes.extend(get_guan_infoes(db_session, guan_id))
    guan_info_ids = [guan_info.id for guan_info in guan_infoes]
    guan_answers = []
    for guan_info_id in guan_info_ids:
        guan_answer = get_guan_answer(db_session, user_id, guan_info_id)
        if guan_answer:
            guan_answers.append(guan_answer)
    answer_info_ids = [guan_answer.answer_info_id for guan_answer in guan_answers]
    answer_infoes = get_answer_infoes_by_ids(db_session, answer_info_ids)

    guan_name_dict = {guan.id: guan.name for guan in guanguan}
    evaluation_result = []
    for answer_info in answer_infoes:
        evaluation = answer_info.answer_evaluation
        if guan_type_id == GUAN_TYPE_ID_MEET:
            evaluation = guan_name_dict.get(answer_info.guan_id, '') + '：' + evaluation
        evaluation_result.append(evaluation)

    return evaluation_result
