#! /usr/bin/env python
# -*- coding: utf-8 -*- 
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from util.monitor import super_monitor


class IdentificationHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取验证
        :param args:
        :param kwargs:
        :return:
        """
        email = self.get_request_parameter('email', para_type=str)
        mobile = self.get_request_parameter('mobile', para_type=str)
        # todo 短信或邮箱验证逻辑
        return self.response(
            resp_json={
                'email': email,
                'mobile': mobile,
            }
        )

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """
        发邮件或短信验证
        :param args:
        :param kwargs:
        :return:
        """
        email = self.get_request_parameter('email', para_type=str)
        mobile = self.get_request_parameter('mobile', para_type=str)
        # todo 短信或邮箱验证逻辑
        return self.response(
            resp_json={
                'email': email,
                'mobile': mobile,
            }
        )