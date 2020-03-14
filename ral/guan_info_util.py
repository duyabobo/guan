#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from dal.answer_info import get_answer_infoes
from dal.guan_answer import get_guan_answers_by_answer_info_id
from dal.guan_answer import get_user_info_from_guan_answer
from dal.guan_info import get_guan_infoes
from dal.guanguan import get_guanguan
from dal.offline_meeting import get_offline_meeting_by_guan_id
from util.const import GUAN_TYPE_ID_MEET
from util.const import SEX_DICT


def get_guan_info_dict(db_session, guan_id):
    """
    从 db 计算 guan_info_dict
    :param db_session:
    :param guan_id:
    :return:
    """
    step = 0  # todo 2.0 版本以后，不一定每次都是0
    guanguan = get_guanguan(db_session, guan_id)
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
        'guan_type_id': guanguan.guan_type_id,
        'step': step,
        'total_step': total_step,
        'question_dict': question_dict,
        'answer_dict': answer_dict
    }


def update_guan_info_dict(db_session, user_id, guan_id, guan_info_dict):
    """
    更新一下 guan_info_dict，增加每一个 guan_info 的 每一个 question_info 的 could_answer/ answer_user_id
    :param db_session:
    :param user_id:
    :param guan_id:
    :param guan_info_dict:
    :return:
    """
    guanguan = get_guanguan(db_session, guan_id)
    if guanguan.guan_type_id == GUAN_TYPE_ID_MEET:
        offline_meeting = get_offline_meeting_by_guan_id(db_session, guan_id)
        guan_info_dict['meeting_time'] = str(offline_meeting.time)
        guan_info_dict['meeting_address'] = str(offline_meeting.address)

        user_info_from_guan_answer = get_user_info_from_guan_answer(db_session, user_id)
        sex = SEX_DICT[user_info_from_guan_answer.answer_info_id]
        for index in guan_info_dict['answer_dict']:
            answers = guan_info_dict['answer_dict'][index]
            for answer in answers:
                could_answer = 0
                answer_user_id = 0
                self_answer = 0
                answer_key = answer['answer_key']
                answer_info_id = answer['answer_info_id']
                if True:  # sex in answer_key:
                    could_answer = 1
                guan_answers = get_guan_answers_by_answer_info_id(
                    db_session, answer_info_id, user_id)  # 隐藏一下涉及社交的逻辑
                if guan_answers:
                    answer_user_id = guan_answers[0].user_id
                    if int(user_id) != answer_user_id:
                        could_answer = 1
                        answer_user_id = 0  # 隐藏一下涉及社交的逻辑
                    else:
                        self_answer = 1
                answer['could_answer'] = could_answer  # 是否可以点击
                answer['answer_user_id'] = answer_user_id  # 已经被哪个用户点击
                answer['self_answer'] = self_answer  # 是否是自己点击过了
