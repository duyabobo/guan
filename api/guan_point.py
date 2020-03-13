#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guan_point import add_guan_point
from dal.guan_point import get_guan_point_by_uid_and_guan_id
from dal.guanguan import get_guanguan
from dal.user import update_guan_point_of_user_info
from ral.guan_point import update_answer_user_cnt
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
        user_id = self.current_user_id
        guan_id = self.get_request_parameter('guan_id', para_type=int)

        guan_point = get_guan_point_by_uid_and_guan_id(self.db_session, user_id, guan_id)
        if not guan_point:
            guanguan = get_guanguan(self.db_session, guan_id)
            update_guan_point_of_user_info(self.db_session, user_id, guanguan.guan_point)
            guan_point = add_guan_point(self.db_session, user_id, guan_id, guanguan.guan_point)
            update_answer_user_cnt(self.redis, self.db_session, guan_id)
        return self.response(
            resp_json={
                'guan_point_id': guan_point.id,
                'information_1': '',  # 1，参与关关在线问答，可以获取积分。
                'information_2': '',  # 2，参加关关线下活动，需要扣除积分。
            }
        )
