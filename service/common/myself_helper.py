#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.verify import VerifyModel
from service.common.selector import selectorFactory
from util.class_helper import lazy_property
from util.const.match import *

OP_FUNCS_DICT = {   # 不同类型的用户，需要维护不通的信息
    MODEL_MAIL_TYPE_UNKNOWN: [],
    MODEL_MAIL_TYPE_SCHOOL: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
        OP_TYPE_MONTH_PAY,
        OP_TYPE_MARTIAL_STATUS,
        OP_TYPE_EDUCATION,
    ],
    MODEL_MAIL_TYPE_WORK: [
        OP_TYPE_SEX,
        OP_TYPE_BIRTH_YEAR,
        OP_TYPE_HEIGHT,
        OP_TYPE_WEIGHT,
    ]
}


class UserHelper(object):

    def __init__(self, user):
        self.user = user

    @lazy_property
    def verify_record(self):
        return VerifyModel.getByPassportId(self.user.passportId)

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

    def getUpdateParams(self, opType, valueIndex):
        updateParams = {}
        if opType == OP_TYPE_SEX and int(valueIndex) != MODEL_SEX_UNKNOWN_INDEX:
            updateParams['sex'] = SEX_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_BIRTH_YEAR:
            updateParams['birth_year'] = BIRTH_YEAR_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_MARTIAL_STATUS:
            updateParams['martial_status'] = MARTIAL_STATUS_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_HEIGHT:
            updateParams['height'] = HEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_WEIGHT:
            updateParams['weight'] = WEIGHT_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_MONTH_PAY:
            updateParams['month_pay'] = MONTH_PAY_CHOICE_LIST[int(valueIndex)]
        elif opType == OP_TYPE_EDUCATION:
            updateParams['education'] = EDUCATION_CHOICE_LIST[int(valueIndex)]
        return updateParams
