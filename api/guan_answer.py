#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/27'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from ral.guan_evaluation import set_evaluation_result
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

        ret = set_evaluation_result(self.redis, user_id, answer_id)  # todo 回答关关问题
        return self.response(
            resp_json={'ret': ret}
        )
