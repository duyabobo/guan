#!/usr/bin/python
# -*- coding=utf-8 -*-
from util.const.base import *
from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR

# model
# MODEL_STATUS_ENUMERATE
MODEL_STATUS_YES = 1
MODEL_STATUS_NO = 0
# MODEL_WORK_VERIFY_STATUS_ENUMERATE
MODEL_WORK_VERIFY_STATUS_YES = 1
MODEL_WORK_VERIFY_STATUS_NO = 0
# MODEL_SEX_ENUMERATE
MODEL_SEX_UNKNOWN_INDEX = 0
MODEL_SEX_MALE_INDEX = 1
MODEL_SEX_FEMALE_INDEX = 2
# OP_TYPE_ENUMERATE  如果更改，需要同步小程序对应枚举
OP_TYPE_SEX = 'updateSex'
OP_TYPE_BIRTH_YEAR = 'updateBirthYear'
OP_TYPE_MARTIAL_STATUS = 'updateMartialStatus'
OP_TYPE_HEIGHT = 'updateHeight'
OP_TYPE_WEIGHT = 'updateWeight'
OP_TYPE_MONTH_PAY = 'updateMonthPay'
OP_TYPE_EDUCATION = 'updateEducation'
OP_BIRTH_YEAR_PERIOD = 'updateBirthYearPeriod'
OP_TYPE_HEIGHT_PERIOD = 'updateHeightPeriod'
OP_TYPE_WEIGHT_PERIOD = 'updateWeightPeriod'
OP_TYPE_MONTH_PAY_PERIOD = 'updateMonthPayPeriod'
OP_TYPE_EDUCATION_PERIOD = 'updateEducationPeriod'
# CHOICE_LIST and DEFAULT_INDEX
SEX_CHOICE_LIST = ["未知", "男", "女"]
DEFAULT_SEX_INDEX = 0

BIRTH_YEAR_CHOICE_LIST = range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR - MIN_AGE + 1)
DEFAULT_YEAR_INDEX = BIRTH_YEAR_CHOICE_LIST.index(DEFAULT_BIRTH_YEAR)

MARTIAL_STATUS_CHOICE_LIST = ["未知", "未婚", "离异"]
DEFAULT_MARTIAL_STATUS_INDEX = 0

HEIGHT_CHOICE_LIST = range(MIN_HEIGHT, MAX_HEIGHT)
DEFAULT_HEIGHT_INDEX = 30

WEIGHT_CHOICE_LIST = range(MIN_WEIGHT, MAX_WEIGHT)
DEFAULT_WEIGHT_INDEX = 20

MONTH_PAY_CHOICE_LIST = range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000)
DEFAULT_MONTH_PAY_INDEX = 6

EDUCATION_CHOICE_LIST = ["未知", "高中", "专科", "本科", "硕士", "博士"]
DEFAULT_EDUCATION_INDEX = 0

MATCH_INFO_DICT = {
    OP_TYPE_SEX: {
        "CHOICE_LIST": SEX_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_SEX_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_MARTIAL_STATUS: {
        "CHOICE_LIST": MARTIAL_STATUS_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_MARTIAL_STATUS_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_BIRTH_YEAR: {
        "CHOICE_LIST": BIRTH_YEAR_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_YEAR_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_HEIGHT: {
        "CHOICE_LIST": HEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_HEIGHT_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_WEIGHT: {
        "CHOICE_LIST": WEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_WEIGHT_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_MONTH_PAY: {
        "CHOICE_LIST": MONTH_PAY_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_MONTH_PAY_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_EDUCATION: {
        "CHOICE_LIST": EDUCATION_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_EDUCATION_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_BIRTH_YEAR_PERIOD: {
        "CHOICE_LIST": BIRTH_YEAR_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_YEAR_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_HEIGHT_PERIOD: {
        "CHOICE_LIST": HEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_HEIGHT_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_WEIGHT_PERIOD: {
        "CHOICE_LIST": WEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_WEIGHT_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_MONTH_PAY_PERIOD: {
        "CHOICE_LIST": MONTH_PAY_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_MONTH_PAY_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_EDUCATION_PERIOD: {
        "CHOICE_LIST": EDUCATION_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_EDUCATION_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    }
}

MODEL_USER_OP_TYPE_EXTEND_1 = 'updateExtend1'
MODEL_USER_OP_TYPE_EXTEND_2 = 'updateExtend2'
MODEL_USER_OP_TYPE_EXTEND_3 = 'updateExtend3'
MODEL_USER_OP_TYPE_EXTEND_4 = 'updateExtend4'
MODEL_USER_OP_TYPE_EXTEND_5 = 'updateExtend5'
MODEL_USER_OP_TYPE_EXTEND_6 = 'updateExtend6'
MODEL_USER_OP_TYPE_EXTEND_7 = 'updateExtend7'
MODEL_USER_OP_TYPE_EXTEND_8 = 'updateExtend8'
MODEL_USER_OP_TYPE_EXTEND_9 = 'updateExtend9'
MODEL_USER_OP_TYPE_EXTEND_10 = 'updateExtend10'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_1 = 'updatePeriodExtend1'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_2 = 'updatePeriodExtend2'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_3 = 'updatePeriodExtend3'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_4 = 'updatePeriodExtend4'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_5 = 'updatePeriodExtend5'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_6 = 'updatePeriodExtend6'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_7 = 'updatePeriodExtend7'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_8 = 'updatePeriodExtend8'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_9 = 'updatePeriodExtend9'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_10 = 'updatePeriodExtend10'

# MEET_RESULT
MODEL_MEET_RESULT_CHOICE_LIST = [x[1] for x in sorted(MODEL_MEET_RESULT_MAP.items(), key=lambda i:i[0])]
