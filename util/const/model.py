#!/usr/bin/python
# -*- coding=utf-8 -*-
from util.const.base import *

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
# MODEL_USER_OP_TYPE_ENUMERATE  如果更改，需要同步小程序对应枚举
MODEL_USER_OP_TYPE_SEX = 'updateSex'
MODEL_USER_SEX_CHOICE_LIST = ["未知", "男", "女"]
MODEL_USER_DEFAULT_SEX_INDEX = 0

MODEL_USER_OP_TYPE_BIRTH_YEAR = 'updateBirthYear'
MODEL_USER_DEFAULT_BIRTH_YEAR = CURRENT_YEAR - GOOD_AGE
MODEL_USER_BIRTH_YEAR_START = CURRENT_YEAR - MAX_AGE
MODEL_USER_BIRTH_YEAR_END = CURRENT_YEAR - MIN_AGE + 1
MODEL_USER_BIRTH_YEAR_CHOICE_LIST = range(MODEL_USER_BIRTH_YEAR_START, MODEL_USER_BIRTH_YEAR_END)
MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX = MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(CURRENT_YEAR - GOOD_AGE)

MODEL_USER_OP_TYPE_MARTIAL_STATUS = 'updateMartialStatus'
MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX = 0
MODEL_USER_MARTIAL_STATUS_CHOICE_LIST = ["未知", "未婚", "离异"]
MODEL_USER_MARTIAL_STATUS_PERIOD_CHOICE_LIST = ["不限", "未婚", "离异"]

MODEL_USER_OP_TYPE_HEIGHT = 'updateHeight'
MODEL_USER_HEIGHT_CHOICE_LIST = range(MIN_HEIGHT, MAX_HEIGHT)
MODEL_USER_DEFAULT_HEIGHT_INDEX = 30

MODEL_USER_OP_TYPE_WEIGHT = 'updateWeight'
MODEL_USER_WEIGHT_CHOICE_LIST = range(MIN_WEIGHT, MAX_WEIGHT)
MODEL_USER_DEFAULT_WEIGHT_INDEX = 20

MODEL_USER_OP_TYPE_MONTH_PAY = 'updateMonthPay'
MODEL_USER_MONTH_PAY_CHOICE_LIST = range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000)
MODEL_USER_DEFAULT_MONTH_PAY_INDEX = 6

MODEL_USER_OP_TYPE_EDUCATION = 'updateEducation'
MODEL_USER_DEFAULT_EDUCATION_INDEX = 0
MODEL_USER_EDUCATION_CHOICE_LIST = ["未知", "高中", "专科", "本科", "硕士", "博士"]  # 如果有改动这个枚举，需要刷数据

MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD = 'updateBirthYearPeriod'

MODEL_USER_OP_TYPE_HEIGHT_PERIOD = 'updateHeightPeriod'
MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST = range(MIN_HEIGHT, MAX_HEIGHT)

MODEL_USER_OP_TYPE_WEIGHT_PERIOD = 'updateWeightPeriod'
MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST = range(MIN_WEIGHT, MAX_WEIGHT)

MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD = 'updateMonthPayPeriod'
MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST = range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000)

MODEL_USER_OP_TYPE_EDUCATION_PERIOD = 'updateEducationPeriod'
MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST = ["不限", "高中", "专科", "本科", "硕士", "博士"]  # 如果有改动这个枚举，需要刷数据

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
