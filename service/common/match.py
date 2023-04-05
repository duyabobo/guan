#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.requirement import UNREACHABLE_REQUIREMENT
from util.const.base import ALL_STR
from util.const.match import MODEL_MAIL_TYPE_UNKNOWN


class MatchHelper(object):

    @staticmethod
    def match(userInfo, requirement):
        """对比 requirement 和 userInfo，进行一个匹配与否的判断"""
        # 1，如果 requirement为None，可以匹配；如果requirement为不可满足的期望，不可匹配
        if requirement is None:
            return True
        if requirement is UNREACHABLE_REQUIREMENT:
            return False
        # 2，未登录，全部返回匹配
        if userInfo is None:
            return True
        # 3，对比 requirement的每一个字段，只有所有字段要求，当前用户都符合，才算匹配
        # 性别
        if userInfo.sex != requirement.sex:
            return False
        # 婚姻
        if userInfo.martial_status >= requirement.martial_status:
            return False
        # 出生年份
        if userInfo.birth_year < requirement.min_birth_year or userInfo.birth_year > requirement.max_birth_year:
            return False
        # 身高
        if userInfo.height < requirement.min_height or userInfo.height > requirement.max_height:
            return False
        # 体重
        if userInfo.weight < requirement.min_weight or userInfo.weight > requirement.max_weight:
            return False
        # 月收入
        if userInfo.month_pay < requirement.min_month_pay or userInfo.month_pay > requirement.max_month_pay:
            return False
        # 籍贯
        if userInfo.home_province != requirement.home_province and requirement.home_province != ALL_STR:
            return False
        if userInfo.home_city != requirement.home_city and requirement.home_city != ALL_STR:
            return False
        if userInfo.home_area != requirement.home_area and requirement.home_area != ALL_STR:
            return False
        # 学校地址
        if userInfo.study_province != requirement.study_province and requirement.study_province != ALL_STR:
            return False
        if userInfo.study_city != requirement.study_city and requirement.study_city != ALL_STR:
            return False
        if userInfo.study_area != requirement.study_area and requirement.study_area != ALL_STR:
            return False
        # 学校
        if userInfo.school_id and userInfo.school_id != requirement.school_id:
            return False
        if userInfo.education_level < requirement.education_level:
            return False
        if userInfo.major != requirement.major and requirement.major != ALL_STR:
            return False
        # 认证类型
        if userInfo.verify_type != requirement.verify_type and requirement.verify_type != MODEL_MAIL_TYPE_UNKNOWN:
            return False
        # 工作地址
        if userInfo.work_province != requirement.work_province and requirement.work_province != ALL_STR:
            return False
        if userInfo.work_city != requirement.work_city and requirement.work_city != ALL_STR:
            return False
        if userInfo.work_area != requirement.work_area and requirement.work_area != ALL_STR:
            return False
        # 职业
        if userInfo.profession != requirement.profession and requirement.profession != ALL_STR:
            return False
        if userInfo.industry != requirement.industry and requirement.industry != ALL_STR:
            return False
        if userInfo.position != requirement.position and requirement.position != ALL_STR:
            return False
        return True
