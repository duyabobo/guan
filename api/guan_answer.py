#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guan_answer import add_guan_answer
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
        answer_id = self.get_request_parameter('answer_id', para_type=int)

        ret = add_guan_answer(self.db_session, user_id, answer_id)
        return self.response(
            resp_json={'ret': ret.id}
        )
