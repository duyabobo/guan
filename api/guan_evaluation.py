#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/24'
# 关关问答结果
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guan_type import get_guan_types
from ral.guan_evaluation import get_evaluation_result
from util.monitor import super_monitor


class GuanEvaluationHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取 guan_evaluation 信息
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user_id
        answer_user_id = self.get_request_parameter('answer_user_id', para_type=int)
        if answer_user_id:
            user_id = answer_user_id

        guan_evaluations = []
        guan_types = get_guan_types(self.db_session)
        guan_type_dict = {guan_type.id: guan_type.name for guan_type in guan_types}
        for guan_type_id in guan_type_dict:
            type_str = guan_type_dict[guan_type_id]
            evaluation_result = get_evaluation_result(
                self.redis, self.db_session, user_id, guan_type_id
            )
            guan_evaluations.append({
                'guan_type': type_str,
                'guan_evaluation_results': evaluation_result
            })
        return self.response(
            resp_json={'guan_evaluations': guan_evaluations}
        )
