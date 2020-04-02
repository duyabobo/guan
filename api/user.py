#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/29'

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.user import get_user_by_user_id
from util.monitor import super_monitor


class UserHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        查询用户的积分
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user_id

        user = get_user_by_user_id(self.db_session, user_id)
        return self.response(
            resp_json={
                'guan_point': user.guan_point,
                'information_1': '1，参与关关在线问答，可以获取积分。',
                'information_2': '2，参加关关线下活动，需要扣除积分。',
                'point_background': 'http://img.ggjjzhzz.cn/point_background.png',
            }
        )
