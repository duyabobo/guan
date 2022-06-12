#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.base import *
from util.const.mini_program import PICKER_TYPE_SELECTOR, PICKER_TYPE_MULTI_SELECTOR

OP_TYPE_SEX = 'updateSex'
OP_TYPE_BIRTH_YEAR = 'updateBirthYear'
OP_TYPE_MARTIAL_STATUS = 'updateMartialStatus'
OP_TYPE_HEIGHT = 'updateHeight'
OP_TYPE_WEIGHT = 'updateWeight'
OP_TYPE_MONTH_PAY = 'updateMonthPay'
OP_TYPE_EDUCATION = 'updateEducation'
OP_TYPE_BIRTH_YEAR_PERIOD = 'updateBirthYearPeriod'
OP_TYPE_HEIGHT_PERIOD = 'updateHeightPeriod'
OP_TYPE_WEIGHT_PERIOD = 'updateWeightPeriod'
OP_TYPE_MONTH_PAY_PERIOD = 'updateMonthPayPeriod'
OP_TYPE_EDUCATION_PERIOD = 'updateEducationPeriod'

MODEL_CONST_MATCH_DICT = {
    OP_TYPE_SEX: {
        "CHOICE_LIST": ["未知", "男", "女"],
        "DEFAULT_INDEX": 0,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
    },
    OP_TYPE_BIRTH_YEAR: {
        "CHOICE_LIST": range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR - MIN_AGE + 1),
        "DEFAULT_INDEX": range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR - MIN_AGE + 1).index(CURRENT_YEAR - GOOD_AGE),
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
    },
    OP_TYPE_HEIGHT: {
        "CHOICE_LIST": range(MIN_HEIGHT, MAX_HEIGHT),
        "DEFAULT_INDEX": 30,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
    },
    OP_TYPE_WEIGHT: {
        "CHOICE_LIST": range(MIN_WEIGHT, MAX_WEIGHT),
        "DEFAULT_INDEX": 20,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
    },
    OP_TYPE_MONTH_PAY: {
        "CHOICE_LIST": range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000),
        "DEFAULT_INDEX": 6,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
    },
    OP_TYPE_EDUCATION: {
        "CHOICE_LIST": ["未知", "高中", "专科", "本科", "硕士", "博士"],
        "DEFAULT_INDEX": 0,
        "PICKER_TYPE": PICKER_TYPE_SELECTOR,
    },
    OP_TYPE_BIRTH_YEAR_PERIOD: {
        "CHOICE_LIST": range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR - MIN_AGE + 1),
        "DEFAULT_INDEX": range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR - MIN_AGE + 1).index(CURRENT_YEAR - GOOD_AGE),
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
    },
    OP_TYPE_HEIGHT_PERIOD: {
        "CHOICE_LIST": range(MIN_HEIGHT, MAX_HEIGHT),
        "DEFAULT_INDEX": 30,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
    },
    OP_TYPE_WEIGHT_PERIOD: {
        "CHOICE_LIST": range(MIN_WEIGHT, MAX_WEIGHT),
        "DEFAULT_INDEX": 20,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
    },
    OP_TYPE_MONTH_PAY_PERIOD: {
        "CHOICE_LIST": range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000),
        "DEFAULT_INDEX": 6,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
    },
    OP_TYPE_EDUCATION_PERIOD: {
        "CHOICE_LIST": ["不限", "高中", "专科", "本科", "硕士", "博士"],
        "DEFAULT_INDEX": 0,
        "PICKER_TYPE": PICKER_TYPE_MULTI_SELECTOR,
    }
}
