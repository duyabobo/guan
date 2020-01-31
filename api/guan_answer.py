#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.answer_info import get_answer_info
from dal.guan_answer import add_guan_answer
from dal.guan_answer import get_guan_answer
from dal.guan_answer import update_guan_answer
from dal.guanguan import get_guanguan
from dal.user import get_user_by_user_id
from ral.guan_evaluation import set_evaluation_result
from ral.guan_evaluation_util import get_evaluation_result_list
from util.const import RESP_GUAN_POINT_NOT_ENOUGH
from util.database import object_to_json
from util.monitor import super_monitor


class GuanAnswerHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """
        回答关关问答
        todo: 如果是线下见面类关关，需要检查一下回答是否符合要求（性别检测，重复选中检测）
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user['id']
        answer_info_id = self.get_request_parameter('answer_info_id', para_type=int)
        guan_id = self.get_request_parameter('guan_id', para_type=int)

        user = get_user_by_user_id(self.db_session, user_id)
        guanguan = get_guanguan(self.db_session, guan_id)
        if user.guan_point + guanguan.guan_point < 0:
            return self.response(
                resp_json={
                    'guan_answer_id': 0
                },
                resp_normal=RESP_GUAN_POINT_NOT_ENOUGH
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
        guan_type_id = guanguan.guan_type_id
        evaluation_result = get_evaluation_result_list(self.db_session, user_id, guan_type_id)
        set_evaluation_result(self.redis, user_id, guan_type_id, evaluation_result)
        return self.response(
            resp_json={
                'guan_answer_id': guan_answer.id
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
        user_id = self.current_user['id']
        guan_info_id = self.get_request_parameter('guan_info_id', para_type=int)

        guan_answer = get_guan_answer(self.db_session, user_id, guan_info_id)
        return self.response(
            resp_json=object_to_json(guan_answer)
        )
