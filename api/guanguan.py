#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/19'

from tornado.concurrent import run_on_executor

from api.basehandler import BaseHandler
from dal.answer_info import add_answer_info
from dal.guan_info import add_guan_info
from dal.guan_point import get_guan_points_by_uid
from dal.guan_type import get_guan_types
from dal.guanguan import add_guanguan
from dal.guanguan import get_guanguan_list
from dal.offline_meeting import get_offline_meetings_by_guan_ids
from ral.guan_info import set_guan_info
from ral.guan_info_util import get_guan_info_dict
from ral.guan_point import get_answer_user_cnt_dict
from util.const import GUAN_TYPE_ID_MEET
from util.monitor import auth_checker
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
                'guan_type_id': guanguan.guan_type_id,
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

    @run_on_executor
    @super_monitor
    @auth_checker('admin')
    def post(self, *args, **kwargs):
        """
        增加 guanguan 信息，后台管理
        :param args:
        :param kwargs:
        :return:
        """
        name = self.get_request_parameter('name', para_type=str)
        guan_type_id = self.get_request_parameter('guan_type_id', para_type=int)
        guan_point = self.get_request_parameter('guan_point', para_type=int)
        guan_infoes = self.get_request_parameter('guan_infoes', para_type=list)

        guanguan = add_guanguan(self.db_session, name, guan_type_id, guan_point)
        guan_id = guanguan.id
        for guan_info in guan_infoes:
            question = guan_info['question']
            guan_info = add_guan_info(self.db_session, guan_id, question)
            answers = guan_info['answers']
            for answer in answers:
                answer_key = answer['answer_key']
                answer_evaluation = answer['answer_evaluation']
                add_answer_info(
                    self.db_session, guan_id, guan_info.id, answer_key, answer_evaluation
                )

        guan_info_dict = get_guan_info_dict(self.db_session, guan_id)
        set_guan_info(self.redis, guan_id, guan_info_dict)

        return self.response(
            resp_json={
                'user_id': 1
            }
        )
