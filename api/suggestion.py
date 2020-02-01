#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/2/1'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.suggestion import add_suggestion
from util.monitor import super_monitor


class SuggestionHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """
        记录用户意见数据
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user['id']
        suggestion_content = self.get_request_parameter('suggestion_content', para_type=str)

        suggestion = add_suggestion(self.db_session, user_id, suggestion_content)
        return self.response(
            resp_json={
                'suggestion_id': suggestion.id
            }
        )
