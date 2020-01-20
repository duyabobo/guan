#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/20'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from ral.guan_info import get_guan_info
from ral.guan_info import set_guan_info
from util.monitor import super_monitor


class GuanInfoHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取 guan_info 信息
        :param args:
        :param kwargs:
        :return:
        """
        guan_id = self.get_request_parameter('guan_id', para_type=int)
        guan_info = get_guan_info(self.redis, guan_id)
        return self.response(
            resp_json=guan_info
        )

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """
        保存 guan_info 信息
        :param args:
        :param kwargs:
        :return:
        """
        guan_id = self.get_request_parameter('guan_id', para_type=int)
        ret = set_guan_info(self.redis, guan_id)
        return self.response(
            resp_json={'ret': ret}
        )
