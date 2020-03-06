#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/3/6'
from api.basehandler import BaseHandler
from util.monitor import super_monitor


class IndexHandler(BaseHandler):
    __model__ = ''

    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取pc页面首页
        :param args:
        :param kwargs:
        :return:
        """
        return self.render('index.html')
