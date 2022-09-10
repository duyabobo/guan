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
        updateParams = {}
        # 单项选择器
        if opType == OP_TYPE_SEX and value != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = value
        elif opType == OP_TYPE_BIRTH_YEAR:
            updateParams['birth_year'] = BIRTH_YEAR_CHOICE_LIST[value]
        elif opType == OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = value
        elif opType == OP_TYPE_HEIGHT:
            updateParams['height'] = HEIGHT_CHOICE_LIST[value]
        elif opType == OP_TYPE_WEIGHT:
            updateParams['weight'] = WEIGHT_CHOICE_LIST[value]
        elif opType == OP_TYPE_MONTH_PAY:
            updateParams['month_pay'] = MONTH_PAY_CHOICE_LIST[value]
        elif opType == OP_TYPE_STUDY_FROM_YEAR:
            updateParams['study_from_year'] = STUDY_FROM_YEAR_CHOICE_LIST[value]
        # region地址选择器类型
        elif opType == OP_TYPE_HOME_REGION:
            updateParams['home_region_id'] = RegionModel.getIdByRegion(*value)
        elif opType == OP_TYPE_STUDY_REGION:
            study_region_id = RegionModel.getIdByRegion(*value)
            updateParams['study_region_id'] = study_region_id
            updateParams['education_id'] = EducationModel.getIdByData(ALL_STR, ALL_STR, ALL_STR)
        elif opType == OP_TYPE_WORK_REGION:
            work_region_id = RegionModel.getIdByRegion(*value)
            updateParams['work_region_id'] = work_region_id
            updateParams['work_id'] = WorkModel.getIdByData(ALL_STR, ALL_STR, ALL_STR)
        # 三项选择器类型
        elif opType == OP_TYPE_EDUCATION_MULTI:
            updateParams['education_id'] = MultiPickerHelper(opType).getChoiceIdAfterConfirm(self.user.education, value)
            delDataIdAfterConfirm(opType, self.user.passport_id)
        elif opType == OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE:
            education_id = MultiPickerHelper(opType).getChoiceIdAfterColumnChanged(self.user, column, value)
            setDataIdAfterColumnChange(opType, self.user.passport_id, education_id)
        elif opType == OP_TYPE_WORK_MULTI:
            updateParams['work_id'] = MultiPickerHelper(opType).getChoiceIdAfterConfirm(self.user.work, value)
            delDataIdAfterConfirm(opType, self.user.passport_id)
        elif opType == OP_TYPE_WORK_MULTI_COLUMN_CHANGE:
            work_id = MultiPickerHelper(opType).getChoiceIdAfterColumnChanged(self.user, column, value)
            setDataIdAfterColumnChange(opType, self.user.passport_id, work_id)
        return updateParams
