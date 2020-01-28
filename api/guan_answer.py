#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.answer_info import get_answer_info
from dal.answer_info import get_answer_infoes
from dal.guan_answer import add_guan_answer
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
        user_id = self.current_user['id']
        answer_info_id = self.get_request_parameter('answer_info_id', para_type=int)

        answer_info = get_answer_info(self.db_session, answer_info_id)
        ret = add_guan_answer(self.db_session, user_id, answer_info.guan_info_id, answer_info_id)
        return self.response(
            resp_json={'ret': ret.id}
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
        guan_info_id = self.get_request_parameter('guan_info_id', para_type=int)

        answer_infoes = get_answer_infoes(self.db_session, guan_info_id)
        resp_json = {
            'answer_infoes': [object_to_json(answer_info) for answer_info in answer_infoes]
        }
        return self.response(
            resp_json=resp_json
        )
