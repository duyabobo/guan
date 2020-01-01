#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from api.basehandler import *
from dal.user_info import get_user_info_by_uid
from dal.user_info import update_user_info 


class UserInfoHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def post(self, *args, **kwargs):
        """用户详细信息完善。
        """
        sex = self.get_request_parameter('sex')
        married_times = self.get_request_parameter('married_times')
        child_num = self.get_request_parameter('child_num')
        age = self.get_request_parameter('age')
        annual_income = self.get_request_parameter('annual_income')
        height = self.get_request_parameter('height')
        weight = self.get_request_parameter('weight')
        degree = self.get_request_parameter('degree')
        seniority = self.get_request_parameter('seniority')
        house_value = self.get_request_parameter('house_value')
        car_value = self.get_request_parameter('car_value')
        home_province = self.get_request_parameter('home_province')
        home_city = self.get_request_parameter('home_city')
        live_province = self.get_request_parameter('live_province')
        live_city = self.get_request_parameter('live_city')
        collage_province = self.get_request_parameter('collage_province')
        collage_city = self.get_request_parameter('collage_city')
        collage = self.get_request_parameter('collage')
        profession = self.get_request_parameter('profession')
        vocation = self.get_request_parameter('vocation')
        user_id = self.current_user['id']

        user_info = get_user_info_by_uid(self.db_session, user_id)
        if not user_info:
            return self.response(resp_normal=RESP_USER_IS_UNKNOWN)
        update_user_info(
            self.db_session,
            user_info,
            sex,
            married_times,
            child_num,
            age,
            annual_income,
            height,
            weight,
            degree,
            seniority,
            house_value,
            car_value,
            home_province,
            home_city,
            live_province,
            live_city,
            collage_province,
            collage_city,
            collage,
            profession,
            vocation
        )
        return self.response(resp_json={'user_id': user_id})
