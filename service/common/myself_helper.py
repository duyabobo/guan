#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.education import EducationModel
from model.region import RegionModel
from model.verify import VerifyModel
from model.work import WorkModel
from ral.multi_picker import setDataIdAfterColumnChange, delDataIdAfterConfirm
from service.common.multi_picker_helper import MultiPickerHelper
from service.common.selector import selectorFactory
from util.class_helper import lazy_property
from util.const.match import *

INFORMATION_PAIR_LIST_DICT = {
    MODEL_MAIL_TYPE_UNKNOWN: [  # 活动详情页，邀请人信息展示顺序
        [OP_TYPE_SEX, OP_TYPE_BIRTH_YEAR],
        [OP_TYPE_HEIGHT, OP_TYPE_WEIGHT],
        [OP_TYPE_EDUCATION_LEVEL, OP_TYPE_MARTIAL_STATUS],
        [OP_TYPE_HOME_REGION],
        [OP_TYPE_STUDY_REGION],
        [OP_TYPE_EDUCATION_MULTI],
    ],
    MODEL_MAIL_TYPE_SCHOOL: [  # 活动详情页，邀请人信息展示顺序
        [OP_TYPE_SEX, OP_TYPE_BIRTH_YEAR],
        [OP_TYPE_HEIGHT, OP_TYPE_WEIGHT],
        [OP_TYPE_EDUCATION_LEVEL, OP_TYPE_MARTIAL_STATUS],
        [OP_TYPE_HOME_REGION],
        [OP_TYPE_STUDY_REGION],
        [OP_TYPE_EDUCATION_MULTI],
    ],
    MODEL_MAIL_TYPE_WORK: [  # 活动详情页，邀请人信息展示顺序
        [OP_TYPE_SEX, OP_TYPE_BIRTH_YEAR],
        [OP_TYPE_HEIGHT, OP_TYPE_WEIGHT],
        [OP_TYPE_MONTH_PAY, OP_TYPE_MARTIAL_STATUS],
        [OP_TYPE_HOME_REGION],
        [OP_TYPE_STUDY_REGION],
        [OP_TYPE_EDUCATION_MULTI],
    ],
}

OP_FUNCS_DICT = {   # 不同类型的用户，需要维护不通的信息
    MODEL_MAIL_TYPE_UNKNOWN: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
        OP_TYPE_MARTIAL_STATUS,
        OP_TYPE_HOME_REGION,
        OP_TYPE_STUDY_REGION,
        OP_TYPE_STUDY_FROM_YEAR,
        OP_TYPE_EDUCATION_LEVEL,
        OP_TYPE_EDUCATION_MULTI,
    ],
    MODEL_MAIL_TYPE_SCHOOL: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
        OP_TYPE_MARTIAL_STATUS,
        OP_TYPE_HOME_REGION,
        OP_TYPE_STUDY_REGION,
        OP_TYPE_STUDY_FROM_YEAR,
        OP_TYPE_EDUCATION_LEVEL,
        OP_TYPE_EDUCATION_MULTI,
    ],
    MODEL_MAIL_TYPE_WORK: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
        OP_TYPE_MARTIAL_STATUS,
        OP_TYPE_HOME_REGION,
        OP_TYPE_EDUCATION_LEVEL,
        OP_TYPE_WORK_REGION,
        OP_TYPE_WORK_MULTI,
        OP_TYPE_MONTH_PAY,
    ]
}


class UserHelper(object):

    def __init__(self, user):
        self.user = user

    @lazy_property
    def verify_record(self):
        return VerifyModel.getByPassportId(self.user.passport_id)

    def getInformationList(self, checkDynamicData):
        informationList = []
        for op_func in OP_FUNCS_DICT.get(self.verify_record.mail_type, []):
            info = selectorFactory(op_func, self.user, checkDynamicData)
            if info:
                informationList.append(info)
        return informationList

    def getInformationPariList(self):
        return INFORMATION_PAIR_LIST_DICT.get(self.verify_record.mail_type, [])

    def getUpdateParams(self, opType, value, column=None):
        userUpdateParams = {}
        requirementUpdateParams = {}
        # 单项选择器
        if opType == OP_TYPE_SEX and value != MODEL_SEX_UNKNOWN_INDEX:
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
        # region地址选择器类型
        elif opType == OP_TYPE_HOME_REGION:
            home_region_id = RegionModel.getIdByRegion(*value)
            userUpdateParams['home_region_id'] = home_region_id
            if not self.user.home_region_id:
                requirementUpdateParams['home_region_id'] = home_region_id
        elif opType == OP_TYPE_STUDY_REGION:
            study_region_id = RegionModel.getIdByRegion(*value)
            userUpdateParams['study_region_id'] = study_region_id
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
