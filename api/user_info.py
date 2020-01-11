#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from datetime import datetime

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.user_info import get_user_info_by_uid
from dal.user_info import update_user_info
from util.const import DEGREE_DICT
from util.const import RESP_USER_IS_UNKNOWN
from util.const import SEX_DICT
from util.monitor import super_monitor


class UserInfoHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """用户详细信息完善。
        """
        sex = self.get_request_parameter('sex')
        age = self.get_request_parameter('age')
        height = self.get_request_parameter('height')
        degree = self.get_request_parameter('degree')
        user_id = self.current_user['id']

        user_info = get_user_info_by_uid(self.db_session, user_id)
        if not user_info:
            return self.response(resp_normal=RESP_USER_IS_UNKNOWN)
        update_user_info(
            self.db_session,
            user_info,
            sex,
            age,
            height,
            degree
        )
        return self.response(resp_json={'user_id': user_id})

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取用户信息
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user['id']

        user_info = get_user_info_by_uid(self.db_session, user_id)
        return self.response(
            resp_json={
                'sex': SEX_DICT.get(user_info.sex, '未知'),
                'age': datetime.now().year - user_info.year_of_birth,
                'degree': DEGREE_DICT.get(user_info.degree, '未知'),
                'height': user_info.height
            }
        )
