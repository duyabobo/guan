#!/usr/bin/python
# -*- coding=utf-8 -*-
from util.const.base import *
from util.const.education import DEFAULT_EDUCATION_MULTI_INDEX
from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR

# model
# MODEL_STATUS_ENUMERATE
MODEL_STATUS_YES = 1
MODEL_STATUS_NO = 0
# MODEL_MAIL_VERIFY_STATUS_ENUMERATE
MODEL_MAIL_VERIFY_STATUS_YES = 1
MODEL_MAIL_VERIFY_STATUS_NO = 0
# MODEL_MARTIAL_STATUS_ENUMERATE
MODEL_MARTIAL_STATUS_UNKNOWN = 0
MODEL_MARTIAL_STATUS_NO_MARRY = 1
MODEL_MARTIAL_STATUS_BREAK = 2
# VERIFY_MAIL_TYPE
MODEL_MAIL_KEYWORD = "edu"
MODEL_MAIL_TYPE_UNKNOWN = 0
MODEL_MAIL_TYPE_SCHOOL = 1
MODEL_MAIL_TYPE_WORK = 2
# MODEL_SEX_ENUMERATE
MODEL_SEX_UNKNOWN_INDEX = 0
MODEL_SEX_MALE_INDEX = 1
MODEL_SEX_FEMALE_INDEX = 2
# MODEL_VERIFY_TYPE
MODEL_VERIFY_TYPE_NO_NEED_VERIFY = 0
MODEL_VERIFY_TYPE_ALL_VERIFY = 1
MODEL_VERIFY_TYPE_SCHOOL = 2
MODEL_VERIFY_TYPE_WORK = 3
# OP_TYPE_ENUMERATE  如果更改，需要同步小程序对应枚举
OP_TYPE_VERIFY = 'updateVerify'
OP_TYPE_SEX = 'updateSex'
OP_TYPE_BIRTH_YEAR = 'updateBirthYear'
OP_TYPE_MARTIAL_STATUS = 'updateMartialStatus'
OP_TYPE_HEIGHT = 'updateHeight'
OP_TYPE_WEIGHT = 'updateWeight'
OP_TYPE_MONTH_PAY = 'updateMonthPay'
OP_TYPE_EDUCATION_MULTI = 'updateEducationMulti'
OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE = 'updateEducationMultiColumnChange'
OP_BIRTH_YEAR_PERIOD = 'updateBirthYearPeriod'
OP_TYPE_HEIGHT_PERIOD = 'updateHeightPeriod'
OP_TYPE_WEIGHT_PERIOD = 'updateWeightPeriod'
OP_TYPE_MONTH_PAY_PERIOD = 'updateMonthPayPeriod'
OP_TYPE_HOME_REGION_PERIOD = 'updateHomeRegionPeriod'
OP_TYPE_STUDY_REGION_PERIOD = 'updateStudyRegionPeriod'
OP_TYPE_HOME_REGION = 'updateHomeRegion'
OP_TYPE_STUDY_REGION = 'updateStudyRegion'
# CHOICE_LIST and DEFAULT_INDEX
VERIFY_CHOICE_LIST = [u"不要求认证", u"教育或工作认证", u"教育认证", u"工作认证"]  # 可以追加元素，但不要改已有元素的顺序。因为数据库存储的枚举值对应这个数组的下标
DEFAULT_VERIFY_INDEX = 0

SEX_CHOICE_LIST = [u"未知", u"男", u"女"]  # 可以追加元素，但不要改已有元素的顺序。因为数据库存储的枚举值对应这个数组的下标
DEFAULT_SEX_INDEX = 0

BIRTH_YEAR_CHOICE_LIST = range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR - MIN_AGE + 1)
DEFAULT_YEAR_INDEX = BIRTH_YEAR_CHOICE_LIST.index(DEFAULT_BIRTH_YEAR)

MARTIAL_STATUS_CHOICE_LIST = [u"未知", u"未婚", u"离异"]  # 可以追加元素，但不要改已有元素的顺序。因为数据库存储的枚举值对应这个数组的下标
DEFAULT_MARTIAL_STATUS_INDEX = 0

HEIGHT_CHOICE_LIST = range(MIN_HEIGHT, MAX_HEIGHT)
DEFAULT_HEIGHT_INDEX = 30

WEIGHT_CHOICE_LIST = range(MIN_WEIGHT, MAX_WEIGHT)
DEFAULT_WEIGHT_INDEX = 20

MONTH_PAY_CHOICE_LIST = range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000)
DEFAULT_MONTH_PAY_INDEX = 6

MATCH_INFO_DICT = {
    OP_TYPE_VERIFY: {
        "CHOICE_LIST": VERIFY_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_VERIFY_INDEX,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
        "COLUMN_CHANGE_FUNC": ""
    },
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
    OP_BIRTH_YEAR_PERIOD: {
        "CHOICE_LIST": BIRTH_YEAR_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_YEAR_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": "birthYearPeriodColumnChange"
    },
    OP_TYPE_HEIGHT_PERIOD: {
        "CHOICE_LIST": HEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_HEIGHT_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": "heightPeriodColumnChange"
    },
    OP_TYPE_WEIGHT_PERIOD: {
        "CHOICE_LIST": WEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_WEIGHT_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": "weightPeriodColumnChange"
    },
    OP_TYPE_EDUCATION_MULTI: {
        "CHOICE_LIST": [],
        "DEFAULT_INDEX": DEFAULT_EDUCATION_MULTI_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": "updateEducationMultiColumnChange",
    },
    OP_TYPE_MONTH_PAY_PERIOD: {
        "CHOICE_LIST": MONTH_PAY_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_MONTH_PAY_INDEX,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
        "COLUMN_CHANGE_FUNC": "monthPayPeriodColumnChange"
    },
}

# MEET_RESULT
MODEL_MEET_RESULT_CHOICE_LIST = [x[1] for x in sorted(MODEL_MEET_RESULT_MAP.items(), key=lambda i:i[0])]
