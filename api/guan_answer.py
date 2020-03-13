#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.answer_info import get_answer_info
from dal.guan_answer import add_guan_answer
from dal.guan_answer import delete_one_guan_answer
from dal.guan_answer import get_guan_answer
from dal.guan_answer import update_guan_answer
from dal.guan_point import get_guan_points_by_uid
from dal.guanguan import get_guanguan
from dal.offline_meeting import get_offline_meeting_by_guan_id
from dal.offline_meeting import get_offline_meetings_by_guan_ids
from dal.user import get_user_by_user_id
from ral.guan_evaluation import set_evaluation_result
from ral.guan_evaluation_util import get_evaluation_result_list
from util.const import GUAN_INFO_ID_USER_INFO
from util.const import GUAN_TYPE_ID_MEET
from util.const import RESP_GUAN_POINT_NOT_ENOUGH
from util.const import RESP_GUAN_TYPE_IS_NOT_MEETING
from util.const import RESP_OFFLINE_MEETING_DUPLICATE
from util.const import RESP_SEX_IS_UNKNOWN
from util.database import object_to_json
from util.monitor import super_monitor


class GuanAnswerHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """
        回答关关问答
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user_id
        answer_info_id = self.get_request_parameter('answer_info_id', para_type=int)
        guan_id = self.get_request_parameter('guan_id', para_type=int)

        guanguan = get_guanguan(self.db_session, guan_id)
        guan_type_id = guanguan.guan_type_id
        if guan_type_id == GUAN_TYPE_ID_MEET:
            user = get_user_by_user_id(self.db_session, user_id)
            if user.guan_point + guanguan.guan_point < 0:
                return self.response(
                    resp_json={
                        'guan_answer_id': 0
                    },
                    resp_normal=RESP_GUAN_POINT_NOT_ENOUGH
                )
            guan_answer = get_guan_answer(self.db_session, user_id, GUAN_INFO_ID_USER_INFO)
            if not guan_answer:
                return self.response(
                    resp_json={
                        'guan_answer_id': 0
                    },
                    resp_normal=RESP_SEX_IS_UNKNOWN
                )
            old_guan_points = get_guan_points_by_uid(self.db_session, user_id)
            old_guan_ids = [guan_point.guan_id for guan_point in old_guan_points]
            offline_meeting = get_offline_meeting_by_guan_id(self.db_session, guan_id)
            old_offline_meetings = get_offline_meetings_by_guan_ids(self.db_session, old_guan_ids)
            for old_offline_meeting in old_offline_meetings:
                if offline_meeting.time.date() == old_offline_meeting.time.date() \
                        and offline_meeting.guan_id != old_offline_meeting.guan_id:
                    return self.response(
                        resp_json={
                            'guan_answer_id': 0
                        },
                        resp_normal=RESP_OFFLINE_MEETING_DUPLICATE
                    )

        answer_info = get_answer_info(self.db_session, answer_info_id)
        guan_info_id = answer_info.guan_info_id
        guan_answer = get_guan_answer(self.db_session, user_id, guan_info_id)
        if guan_answer:
            update_guan_answer(self.db_session, guan_answer, answer_info_id)
        else:
            guan_answer = add_guan_answer(
                self.db_session, user_id, guan_id, guan_info_id, answer_info_id
            )
        evaluation_result = get_evaluation_result_list(self.db_session, user_id, guan_type_id)
        set_evaluation_result(self.redis, user_id, guan_type_id, evaluation_result)
        return self.response(
            resp_json={
                'guan_answer_id': guan_answer.id
            }
        )

    @run_on_executor
    @super_monitor
    def put(self, *args, **kwargs):
        """
        修改关关问答，主要针对线下见面类取消操作
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user_id
        answer_info_id = self.get_request_parameter('answer_info_id', para_type=int)
        guan_id = self.get_request_parameter('guan_id', para_type=int)

        guanguan = get_guanguan(self.db_session, guan_id)
        guan_type_id = guanguan.guan_type_id
        if guan_type_id != GUAN_TYPE_ID_MEET:
            return self.response(
                resp_json={
                    'guan_answer_id': 0
                },
                resp_normal=RESP_GUAN_TYPE_IS_NOT_MEETING
            )
        ret = delete_one_guan_answer(self.db_session, user_id, answer_info_id)
        evaluation_result = get_evaluation_result_list(self.db_session, user_id, guan_type_id)
        set_evaluation_result(self.redis, user_id, guan_type_id, evaluation_result)
        return self.response(
            resp_json={
                'delete_ret': ret
            }
        )

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取关关问答
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user_id
        guan_info_id = self.get_request_parameter('guan_info_id', para_type=int)

        guan_answer = get_guan_answer(self.db_session, user_id, guan_info_id)
        return self.response(
            resp_json=object_to_json(guan_answer)
        )
