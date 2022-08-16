#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/3/6'
from handler.basehandler import BaseHandler
from util.monitor import superMonitor, Response


class IndexHandler(BaseHandler):
    __model__ = ''

    @superMonitor
    def get(self, *args, **kwargs):
        """
        获取pc页面首页
        :param args:
        :param kwargs:
        :return:
        """
        return self.render('index.html')
