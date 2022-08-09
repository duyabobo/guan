#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.region import RegionModel
from model.verify import VerifyModel
from service.common.multi_picker_helper import EducationHelper
from service.common.selector import selectorFactory
from util.class_helper import lazy_property
from util.const.match import *

OP_FUNCS_DICT = {   # 不同类型的用户，需要维护不通的信息
    MODEL_MAIL_TYPE_UNKNOWN: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
        OP_TYPE_MONTH_PAY,
        OP_TYPE_HOME_REGION,
        OP_TYPE_STUDY_REGION,
        OP_TYPE_EDUCATION_MULTI,
        OP_TYPE_MARTIAL_STATUS,
    ],
    MODEL_MAIL_TYPE_SCHOOL: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
        OP_TYPE_HOME_REGION,
        OP_TYPE_STUDY_REGION,
        OP_TYPE_EDUCATION_MULTI,
        OP_TYPE_MARTIAL_STATUS,
    ],
    MODEL_MAIL_TYPE_WORK: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
        OP_TYPE_MONTH_PAY,
        OP_TYPE_HOME_REGION,
        OP_TYPE_STUDY_REGION,
        OP_TYPE_EDUCATION_MULTI,
        OP_TYPE_MARTIAL_STATUS,
    ]
}


class UserHelper(object):

    def __init__(self, user):
        self.user = user

    @lazy_property
    def verify_record(self):
        return VerifyModel.getByPassportId(self.user.passport_id)

    def getInformationList(self):
        informationList = []
        for op_func in OP_FUNCS_DICT.get(self.verify_record.mail_type, []):
            info = selectorFactory(op_func, self.user)
            if info:
                informationList.append(info)
        return informationList

    @property
    def hasFillFinish(self):
        informationList = self.getInformationList()
        return reduce(lambda x, y: x and y, [i.hasFilled for i in informationList])

    def getUpdateParams(self, opType, value, column=None):
        updateParams = {}
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
        elif opType == OP_TYPE_HOME_REGION:
            updateParams['home_region_id'] = RegionModel.getIdByRegion(*value)
        elif opType == OP_TYPE_STUDY_REGION:
            updateParams['study_region_id'] = RegionModel.getIdByRegion(*value)
        elif opType == OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE:
            updateParams['education_id'] = EducationHelper(self.user.study_region).\
                getChoiceIdAfterColumnChanged(self.user.education, column, value)
        return updateParams
