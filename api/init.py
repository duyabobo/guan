#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/2/2'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from util.monitor import super_monitor


class InitHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取小程序页面初始化数据
        :param args:
        :param kwargs:
        :return:
        """
        return self.response(
            resp_json={
                'slogan': '找到好配偶'
            }
        )
