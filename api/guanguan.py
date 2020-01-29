#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/19'

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guan_type import get_guan_types
from dal.guanguan import get_guanguan_list
from util.monitor import super_monitor


class GuanGuanHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取 guanguan 信息  # todo 已回答过的不需要显示，分享赚取积分也是一个关关，并且可以多次操作
        :param args:
        :param kwargs:
        :return:
        """
        guanguan_list = get_guanguan_list(self.db_session)
        guan_types = get_guan_types(self.db_session)
        guan_type_dict = {guan_type.id: guan_type.name for guan_type in guan_types}
        guanguan_list = [
            {
                'id': guanguan.id,
                'name': guanguan.name,
                'guan_type': guan_type_dict.get(guanguan.guan_type_id, '未知'),
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
