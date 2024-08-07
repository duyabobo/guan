#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.education import EducationModel
from model.region import RegionModel
from model.school import UNKNOWN_SCHOOL_ID
from model.work import WorkModel
from ral.multi_picker import setDataIdAfterColumnChange, delDataIdAfterConfirm
from service.common.multi_picker_helper import MultiPickerHelper
from service.common.school_helper import SchoolHelper
from service.common.selector import selectorFactory
from util.const.match import *


OP_FUNC_LIST = [
    OP_TYPE_SEX,
    OP_BIRTH_YEAR_PERIOD,
    OP_TYPE_HEIGHT_PERIOD,
    OP_TYPE_WEIGHT_PERIOD,
    # OP_TYPE_MARTIAL_STATUS_PERIOD,
    OP_TYPE_HOME_REGION_PERIOD,
    # OP_TYPE_NONE,
    OP_TYPE_EDUCATION_LEVEL,
    OP_TYPE_STUDY_REGION_PERIOD,
    OP_TYPE_STUDY_SCHOOL,
    OP_TYPE_STUDY_FROM_YEAR_PERIOD,
    OP_TYPE_EDUCATION_MULTI,
    # OP_TYPE_NONE,
    # OP_TYPE_MONTH_PAY_PERIOD,
    # OP_TYPE_WORK_REGION_PERIOD,
    # OP_TYPE_WORK_MULTI,
]


class RequirementHelper(object):

    def __init__(self, requirement):
        self.requirement = requirement

    def getRequirementList(self, checkDynamicData):
        requirementList = []
        for op_func in OP_FUNC_LIST:
            requirement = selectorFactory(op_func, self.requirement, checkDynamicData)
            if requirement:
                requirementList.append(requirement)
        return requirementList

    def getUpdateParams(self, opType, value, column=None):
        updateParams = {}
        # 单项选择器类型
        if opType == OP_TYPE_SEX and value != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = value
        elif opType == OP_TYPE_EDUCATION_LEVEL:
            updateParams['education_level'] = value
        elif opType == OP_TYPE_STUDY_SCHOOL:
            school_list = SchoolHelper.getSortedSchoolList(regionId=self.requirement.study_region_id)
            school_id_list = [s.id for s in school_list]
            if value > len(school_id_list) - 1:
                school_id = UNKNOWN_SCHOOL_ID
            else:
                school_id = school_id_list[value]
            updateParams['school_id'] = school_id
        # 双项选择器类型
        elif opType == OP_BIRTH_YEAR_PERIOD:
            updateParams['min_birth_year'] = BIRTH_YEAR_CHOICE_LIST[value[0]]
            updateParams['max_birth_year'] = max(BIRTH_YEAR_CHOICE_LIST[value[0]], BIRTH_YEAR_CHOICE_LIST[value[1]])
        elif opType == OP_TYPE_MARTIAL_STATUS_PERIOD:
            updateParams['martial_status'] = value
        elif opType == OP_TYPE_WEIGHT_PERIOD:
            updateParams['min_weight'] = WEIGHT_CHOICE_LIST[value[0]]
            updateParams['max_weight'] = max(WEIGHT_CHOICE_LIST[value[0]], WEIGHT_CHOICE_LIST[value[1]])
        elif opType == OP_TYPE_HEIGHT_PERIOD:
            updateParams['min_height'] = HEIGHT_CHOICE_LIST[value[0]]
            updateParams['max_height'] = max(HEIGHT_CHOICE_LIST[value[0]], HEIGHT_CHOICE_LIST[value[1]])
        elif opType == OP_TYPE_MONTH_PAY_PERIOD:
            updateParams['min_month_pay'] = MONTH_PAY_CHOICE_LIST[value[0]]
            updateParams['max_month_pay'] = max(MONTH_PAY_CHOICE_LIST[value[0]], MONTH_PAY_CHOICE_LIST[value[1]])
        elif opType == OP_TYPE_STUDY_FROM_YEAR_PERIOD:
            updateParams['min_study_from_year'] = STUDY_FROM_YEAR_CHOICE_LIST[value[0]]
            updateParams['max_study_from_year'] = max(STUDY_FROM_YEAR_CHOICE_LIST[value[0]], STUDY_FROM_YEAR_CHOICE_LIST[value[1]])
        # region地址选择器类型
        elif opType == OP_TYPE_HOME_REGION_PERIOD:
            updateParams['home_region_id'] = RegionModel.getIdByRegion(*value)
        elif opType == OP_TYPE_STUDY_REGION_PERIOD:
            study_region_id = RegionModel.getIdByRegion(*value)
            updateParams['study_region_id'] = study_region_id
            if self.requirement.study_region_id != study_region_id:
                updateParams['education_id'] = EducationModel.getIdByData(ALL_STR, ALL_STR, ALL_STR)
                updateParams['school_id'] = UNKNOWN_SCHOOL_ID
        elif opType == OP_TYPE_WORK_REGION_PERIOD:
            work_region_id = RegionModel.getIdByRegion(*value)
            updateParams['work_region_id'] = work_region_id
            updateParams['work_id'] = WorkModel.getIdByData(ALL_STR, ALL_STR, ALL_STR)
        # 三项选择器类型
        elif opType == OP_TYPE_EDUCATION_MULTI:
            updateParams['education_id'] = MultiPickerHelper(opType).getChoiceIdAfterConfirm(self.requirement.education, value)
            delDataIdAfterConfirm(opType, self.requirement.passport_id)
        elif opType == OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE:
            education_id = MultiPickerHelper(opType).getChoiceIdAfterColumnChanged(self.requirement, column, value)
            setDataIdAfterColumnChange(opType, self.requirement.passport_id, education_id)
        elif opType == OP_TYPE_WORK_MULTI:
            updateParams['work_id'] = MultiPickerHelper(opType).getChoiceIdAfterConfirm(self.requirement.education, value)
            delDataIdAfterConfirm(opType, self.requirement.passport_id)
        elif opType == OP_TYPE_WORK_MULTI_COLUMN_CHANGE:
            work_id = MultiPickerHelper(opType).getChoiceIdAfterColumnChanged(self.requirement, column, value)
            setDataIdAfterColumnChange(opType, self.requirement.passport_id, work_id)
        return updateParams
