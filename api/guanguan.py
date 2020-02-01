#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/19'

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.guan_point import get_guan_points_by_uid
from dal.guan_type import get_guan_types
from dal.guanguan import get_guanguan_list
from dal.offline_meeting import get_offline_meetings_by_guan_ids
from ral.guan_point import get_answer_user_cnt_dict
from util.const import GUAN_TYPE_ID_MEET
from util.monitor import super_monitor


class GuanGuanHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """
        获取 guanguan 信息
        :param args:
        :param kwargs:
        :return:
        """
        user_id = self.current_user['id']

        guanguan_list = get_guanguan_list(self.db_session)
        guan_types = get_guan_types(self.db_session)
        guan_type_dict = {guan_type.id: guan_type.name for guan_type in guan_types}
        answers_dict = get_answer_user_cnt_dict(self.redis, self.db_session)
        guan_points = get_guan_points_by_uid(self.db_session, user_id)
        guan_id_set = set([guan_point.guan_id for guan_point in guan_points])
        all_guan_ids = [guanguan.id for guanguan in guanguan_list]
        offline_meetings = get_offline_meetings_by_guan_ids(self.db_session, all_guan_ids)
        offline_meeting_data_dict = {
            o.guan_id: str(o.time) + '，' + o.address + '。活动代号：' for o in offline_meetings
        }
        guanguan_list = [
            {
                'id': guanguan.id,
                'name': offline_meeting_data_dict.get(guanguan.id, '') + guanguan.name,
                'guan_type': guan_type_dict.get(guanguan.guan_type_id, '未知'),
                'guan_point': str(guanguan.guan_point) + '个积分',
                'answers': '%s个参与' % answers_dict.get(str(guanguan.id), 0)
            } for guanguan in guanguan_list
            if guanguan.id not in guan_id_set or guanguan.guan_type_id == GUAN_TYPE_ID_MEET
        ]
        return self.response(
            resp_json={
                'guanguan_list': guanguan_list
            }
        )
