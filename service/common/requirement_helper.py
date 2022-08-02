#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from model.region import RegionModel
from model.verify import VerifyModel
from service.common.selector import selectorFactory
from util.class_helper import lazy_property
from util.const.match import *

OP_FUNCS_DICT = {
    MODEL_MAIL_TYPE_UNKNOWN: [
        OP_TYPE_SEX,
        OP_BIRTH_YEAR_PERIOD,
        OP_TYPE_HEIGHT_PERIOD,
        OP_TYPE_WEIGHT_PERIOD,
        OP_TYPE_HOME_REGION_PERIOD,
        OP_TYPE_MARTIAL_STATUS,
    ],
    MODEL_MAIL_TYPE_SCHOOL: [
        OP_TYPE_SEX,
        OP_BIRTH_YEAR_PERIOD,
        OP_TYPE_HEIGHT_PERIOD,
        OP_TYPE_WEIGHT_PERIOD,
        OP_TYPE_HOME_REGION_PERIOD,
        OP_TYPE_MARTIAL_STATUS,
    ],
    MODEL_MAIL_TYPE_WORK: [
        OP_TYPE_SEX,
        OP_BIRTH_YEAR_PERIOD,
        OP_TYPE_HEIGHT_PERIOD,
        OP_TYPE_WEIGHT_PERIOD,
        OP_TYPE_MONTH_PAY_PERIOD,
        OP_TYPE_EDUCATION_PERIOD,
        OP_TYPE_HOME_REGION_PERIOD,
        OP_TYPE_MARTIAL_STATUS,
    ]
}


class RequirementHelper(object):

    def __init__(self, requirement):
        self.requirement = requirement

    @lazy_property
    def verify_record(self):
        return VerifyModel.getByPassportId(self.requirement.passport_id)
        
    def getRequirementList(self):
        requirementList = []
        for op_func in OP_FUNCS_DICT.get(self.verify_record.mail_type, []):
            requirement = selectorFactory(op_func, self.requirement)
            if requirement:
                requirementList.append(requirement)
        return requirementList

    def getUpdateParams(self, opType, value):
        updateParams = {}
        if opType == OP_TYPE_SEX and value != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = SEX_CHOICE_LIST[value]
        elif opType == OP_BIRTH_YEAR_PERIOD:
            updateParams['min_birth_year'] = BIRTH_YEAR_CHOICE_LIST[value[0]]
            updateParams['max_birth_year'] = BIRTH_YEAR_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = MARTIAL_STATUS_CHOICE_LIST[value]
        elif opType == OP_TYPE_WEIGHT_PERIOD:
            updateParams['min_weight'] = WEIGHT_CHOICE_LIST[value[0]]
            updateParams['max_weight'] = WEIGHT_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_HEIGHT_PERIOD:
            updateParams['min_height'] = HEIGHT_CHOICE_LIST[value[0]]
            updateParams['max_height'] = HEIGHT_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_MONTH_PAY_PERIOD:
            updateParams['min_month_pay'] = MONTH_PAY_CHOICE_LIST[value[0]]
            updateParams['max_month_pay'] = MONTH_PAY_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_EDUCATION_PERIOD:
            updateParams['min_education'] = EDUCATION_CHOICE_LIST[value[0]]
            updateParams['max_education'] = EDUCATION_CHOICE_LIST[value[1]]
        elif opType == OP_TYPE_HOME_REGION_PERIOD:
            updateParams['home_region_id'] = RegionModel.getByRegion(*value)
        return updateParams
