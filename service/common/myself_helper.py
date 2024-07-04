#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.region import RegionModel
from model.school import UNKNOWN_SCHOOL_ID
from ral.multi_picker import setDataIdAfterColumnChange, delDataIdAfterConfirm
from service.common.match import OP_FUNC_LIST
from service.common.multi_picker_helper import MultiPickerHelper
from service.common.school_helper import SchoolHelper
from service.common.selector import selectorFactory
from util.const.match import *


class UserHelper(object):

    def __init__(self, user):
        self.user = user

    def getInformationList(self, checkDynamicData):
        informationList = []
        for op_func in OP_FUNC_LIST:
            info = selectorFactory(op_func, self.user, checkDynamicData)
            if info:
                informationList.append(info)
        return informationList

    def getInformationPariList(self):
        return [[f] for f in OP_FUNC_LIST if f != OP_TYPE_NONE]

    def getUpdateParams(self, opType, value, column=None):
        userUpdateParams = {}
        requirementUpdateParams = {}
        # 单项选择器
        if opType == OP_TYPE_VERIFY and value != MODEL_MAIL_TYPE_UNKNOWN:
            userUpdateParams['verify_type'] = value
            requirementUpdateParams['verify_type'] = value
        elif opType == OP_TYPE_SEX and value != MODEL_SEX_UNKNOWN_INDEX:
            userUpdateParams['sex'] = value
            if self.user.sex == MODEL_SEX_UNKNOWN_INDEX:  # 首次更新用户信息- sex。下同
                if value == MODEL_SEX_MALE_INDEX:
                    requirementUpdateParams['sex'] = MODEL_SEX_FEMALE_INDEX
                elif value == MODEL_SEX_FEMALE_INDEX:
                    requirementUpdateParams['sex'] = MODEL_SEX_MALE_INDEX
        elif opType == OP_TYPE_BIRTH_YEAR:
            userUpdateParams['birth_year'] = BIRTH_YEAR_CHOICE_LIST[value]
            if not self.user.birth_year:
                requirementUpdateParams['min_birth_year'] = BIRTH_YEAR_CHOICE_LIST[max(value-2, 0)]
                requirementUpdateParams['max_birth_year'] = BIRTH_YEAR_CHOICE_LIST[min(value+2, len(BIRTH_YEAR_CHOICE_LIST)-1)]
        elif opType == OP_TYPE_MARTIAL_STATUS:
            userUpdateParams['martial_status'] = value
            requirementUpdateParams['martial_status'] = value
        elif opType == OP_TYPE_MARTIAL_STATUS_PERIOD:
            userUpdateParams['martial_status'] = value
            requirementUpdateParams['martial_status'] = value
        elif opType == OP_TYPE_HEIGHT:
            userUpdateParams['height'] = HEIGHT_CHOICE_LIST[value]
            if not self.user.height:
                requirementUpdateParams['min_height'] = HEIGHT_CHOICE_LIST[value-5]
                requirementUpdateParams['max_height'] = HEIGHT_CHOICE_LIST[value+5]
        elif opType == OP_TYPE_WEIGHT:
            userUpdateParams['weight'] = WEIGHT_CHOICE_LIST[value]
            if not self.user.weight:
                requirementUpdateParams['min_weight'] = WEIGHT_CHOICE_LIST[value-5]
                requirementUpdateParams['max_weight'] = WEIGHT_CHOICE_LIST[value+5]
        elif opType == OP_TYPE_MONTH_PAY:
            userUpdateParams['month_pay'] = MONTH_PAY_CHOICE_LIST[value]
            if not self.user.month_pay:
                requirementUpdateParams['min_month_pay'] = MONTH_PAY_CHOICE_LIST[value-5]
                requirementUpdateParams['max_month_pay'] = MONTH_PAY_CHOICE_LIST[value+5]
        elif opType == OP_TYPE_STUDY_FROM_YEAR:
            userUpdateParams['study_from_year'] = STUDY_FROM_YEAR_CHOICE_LIST[value]
            if not self.user.study_from_year:
                requirementUpdateParams['min_study_from_year'] = STUDY_FROM_YEAR_CHOICE_LIST[value-1]
                requirementUpdateParams['max_study_from_year'] = STUDY_FROM_YEAR_CHOICE_LIST[value+1]
        elif opType == OP_TYPE_EDUCATION_LEVEL:
            userUpdateParams['education_level'] = value
            requirementUpdateParams['education_level'] = value
        elif opType == OP_TYPE_STUDY_SCHOOL:
            school_list = SchoolHelper.getSortedSchoolList(regionId=self.user.study_region_id)
            school_id_list = [s.id for s in school_list]
            if value > len(school_id_list) - 1:
                school_id = UNKNOWN_SCHOOL_ID
            else:
                school_id = school_id_list[value]
            userUpdateParams['school_id'] = school_id
        # region地址选择器类型
        elif opType == OP_TYPE_HOME_REGION:
            home_region_id = RegionModel.getIdByRegion(*value)
            userUpdateParams['home_region_id'] = home_region_id
            if not self.user.home_region_id:
                requirementUpdateParams['home_region_id'] = home_region_id
        elif opType == OP_TYPE_STUDY_REGION:
            study_region_id = RegionModel.getIdByRegion(*value)
            userUpdateParams['study_region_id'] = study_region_id
            if self.user.study_region_id != study_region_id:
                userUpdateParams['school_id'] = UNKNOWN_SCHOOL_ID
            if not self.user.study_region_id:
                requirementUpdateParams['study_region_id'] = study_region_id
        elif opType == OP_TYPE_WORK_REGION:
            work_region_id = RegionModel.getIdByRegion(*value)
            userUpdateParams['work_region_id'] = work_region_id
            if not self.user.work_region_id:
                requirementUpdateParams['work_region_id'] = work_region_id
        # 三项选择器类型
        elif opType == OP_TYPE_EDUCATION_MULTI:
            education_id = MultiPickerHelper(opType).getChoiceIdAfterConfirm(self.user.education, value)
            userUpdateParams['education_id'] = education_id
            delDataIdAfterConfirm(opType, self.user.passport_id)
            if not self.user.education_id:
                requirementUpdateParams['education_id'] = education_id
        elif opType == OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE:
            education_id = MultiPickerHelper(opType).getChoiceIdAfterColumnChanged(self.user, column, value)
            setDataIdAfterColumnChange(opType, self.user.passport_id, education_id)
        elif opType == OP_TYPE_WORK_MULTI:
            work_id = MultiPickerHelper(opType).getChoiceIdAfterConfirm(self.user.work, value)
            userUpdateParams['work_id'] = work_id
            delDataIdAfterConfirm(opType, self.user.passport_id)
            if not self.user.work_id:
                requirementUpdateParams['work_id'] = work_id
        elif opType == OP_TYPE_WORK_MULTI_COLUMN_CHANGE:
            work_id = MultiPickerHelper(opType).getChoiceIdAfterColumnChanged(self.user, column, value)
            setDataIdAfterColumnChange(opType, self.user.passport_id, work_id)
        return userUpdateParams, requirementUpdateParams
