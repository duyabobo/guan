#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/20'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from ral.guan_info import get_guan_info
from dal.guanguan import get_guanguan
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
        user_id = self.current_user['id']

        guan_id = self.get_request_parameter('guan_id', para_type=int)
        guanguan = get_guanguan(self.db_session, guan_id)
        guan_info = get_guan_info(self.redis, self.db_session, user_id, guan_id)
        guan_info.update({'guan_id': guanguan.id, 'guan_point': guanguan.guan_point})

        return self.response(
            resp_json=guan_info
        )
