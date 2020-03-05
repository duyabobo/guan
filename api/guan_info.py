#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/20'
from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guan_answer import get_guan_answer
from dal.guanguan import get_guanguan
from ral.guan_info import get_guan_info
from util.const import GUAN_INFO_ID_USER_INFO
from util.const import GUAN_TYPE_ID_MEET
from util.const import RESP_SEX_IS_UNKNOWN
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
        guan_type_id = guanguan.guan_type_id
        if guan_type_id == GUAN_TYPE_ID_MEET:
            guan_answer = get_guan_answer(self.db_session, user_id, GUAN_INFO_ID_USER_INFO)
            if not guan_answer:
                return self.response(
                    resp_json={
                        'guan_answer_id': 0
                    },
                    resp_normal=RESP_SEX_IS_UNKNOWN
                )
        guan_info = get_guan_info(self.redis, self.db_session, user_id, guan_id)
        guan_info.update({'guan_id': guanguan.id, 'guan_point': guanguan.guan_point})

        return self.response(
            resp_json=guan_info
        )
