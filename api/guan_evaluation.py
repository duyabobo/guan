#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/24'
# 关关问答结果
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from ral.guan_evaluation import get_evaluation_result
from ral.guan_evaluation import set_evaluation_result
from util.const import GUAN_TYPE_DICT
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
        user_id = self.current_user['id']

        guan_evaluations = []
        for guan_type in GUAN_TYPE_DICT:
            type_str = GUAN_TYPE_DICT[guan_type]
            evaluation_result = get_evaluation_result(self.redis, user_id, guan_type)
            guan_evaluations.append({
                'guan_type': type_str,
                'guan_evaluation_results': evaluation_result
            })
        return self.response(
            resp_json={'guan_evaluations': guan_evaluations}
        )

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """
        保存 guan_evaluation 信息，这里是一个便捷接口，正常情况下需要一个异步的分析脚本，把数据测评好然后写入 redis
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user['id']
        guan_type = self.get_request_parameter('guan_type', para_type=int)

        ret = set_evaluation_result(self.redis, user_id, guan_type)
        return self.response(
            resp_json={'ret': ret}
        )
