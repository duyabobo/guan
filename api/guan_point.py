#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guan_point import add_guan_point
from dal.guanguan import get_guanguan
from dal.user import get_user_by_user_id
from dal.user import update_guan_point_of_user_info
from util.monitor import super_monitor


class GuanPointHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """
        记录关关问答积分数据
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user['id']
        guan_id = self.get_request_parameter('guan_id', para_type=int)

        guanguan = get_guanguan(self.db_session, guan_id)
        update_guan_point_of_user_info(self.db_session, user_id, guanguan.guan_point)
        guan_point = add_guan_point(self.db_session, user_id, guan_id, guanguan.guan_point)
        return self.response(
            resp_json={
                'guan_point_id': guan_point.id
            }
        )

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        查询用户的积分
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user['id']

        user = get_user_by_user_id(self.db_session, user_id)
        return self.response(
            resp_json={
                'guan_point': user.guan_point
            }
        )
