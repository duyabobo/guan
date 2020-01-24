#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/19'

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guanguan import get_guanguan_list
from util.const import GUAN_TYPE_DICT
from util.monitor import super_monitor


class GuanGuanHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取 guanguan 信息
        :param args:
        :param kwargs:
        :return:
        """
        guanguan_list = get_guanguan_list(self.db_session)
        guanguan_list = [
            {
                'id': guanguan.id,
                'name': guanguan.name,
                'guan_type': GUAN_TYPE_DICT.get(guanguan.guan_type, '未知'),
                'guan_point': str(guanguan.guan_point) + '个积分',
                'answers': '10个参与',  # todo
                'step': 1,
            } for guanguan in guanguan_list
        ]
        return self.response(
            resp_json={
                'guanguan_list': guanguan_list
            }
        )
