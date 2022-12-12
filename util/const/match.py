#!/usr/bin/python
# -*- coding=utf-8 -*-
from util.const.base import *
from util.const.education import DEFAULT_MULTI_INDEX, EDUCATION_LEVEL, DEFAULT_EDUCATION_INDEX

# model
# MODEL_STATUS_ENUMERATE
MODEL_STATUS_YES = 1
MODEL_STATUS_NO = 0
MODEL_STATUS_EMPTY = -1
# MODEL_ACTIVITY_STATE
MODEL_ACTIVITY_STATE_EMPTY = 0
MODEL_ACTIVITY_STATE_INVITING = 1
MODEL_ACTIVITY_AVALIABLE_STATE_LIST = [MODEL_ACTIVITY_STATE_EMPTY, MODEL_ACTIVITY_STATE_INVITING]
MODEL_ACTIVITY_STATE_INVITE_SUCCESS = 100
# MODEL_MAIL_VERIFY_STATUS_ENUMERATE
MODEL_MAIL_VERIFY_STATUS_YES = 1
MODEL_MAIL_VERIFY_STATUS_NO = 0
# OP_TYPE_ENUMERATE  如果更改，需要同步小程序对应枚举。新增枚举类型，就是在这里增加，然后项目里其他用到枚举的地方都增加支持。最后小程序里对应增加同名的js方法。
OP_TYPE_VERIFY = 'updateVerify'
OP_TYPE_SEX = 'updateSex'
OP_TYPE_BIRTH_YEAR = 'updateBirthYear'
OP_TYPE_MARTIAL_STATUS = 'updateMartialStatus'
OP_TYPE_HEIGHT = 'updateHeight'
OP_TYPE_WEIGHT = 'updateWeight'
OP_TYPE_MONTH_PAY = 'updateMonthPay'
OP_TYPE_EDUCATION_MULTI = 'updateEducationMulti'
OP_TYPE_WORK_MULTI = 'updateWorkMulti'
OP_TYPE_EDUCATION_MULTI_COLUMN_CHANGE = 'updateEducationMultiColumnChange'
OP_TYPE_WORK_MULTI_COLUMN_CHANGE = 'updateWorkMultiColumnChange'
OP_BIRTH_YEAR_PERIOD = 'updateBirthYearPeriod'
OP_TYPE_HEIGHT_PERIOD = 'updateHeightPeriod'
OP_TYPE_WEIGHT_PERIOD = 'updateWeightPeriod'
OP_TYPE_MONTH_PAY_PERIOD = 'updateMonthPayPeriod'
OP_TYPE_HOME_REGION_PERIOD = 'updateHomeRegionPeriod'
OP_TYPE_WORK_REGION_PERIOD = 'updateWorkRegionPeriod'
OP_TYPE_STUDY_REGION_PERIOD = 'updateStudyRegionPeriod'
OP_TYPE_WORK_REGION = 'updateWorkRegion'
OP_TYPE_HOME_REGION = 'updateHomeRegion'
OP_TYPE_STUDY_REGION = 'updateStudyRegion'
OP_TYPE_STUDY_FROM_YEAR = 'updateStudyFromYear'
OP_TYPE_EDUCATION_LEVEL = 'updateEducationLevel'
OP_TYPE_STUDY_FROM_YEAR_PERIOD = 'updateStudyFromYearPeriod'
# CHOICE_LIST and DEFAULT_INDEX

# VERIFY_MAIL_TYPE
MODEL_MAIL_KEYWORD = "edu"
# MODEL_VERIFY_TYPE
MODEL_MAIL_TYPE_UNKNOWN = MODEL_VERIFY_TYPE_NO_NEED_VERIFY = 0
MODEL_MAIL_TYPE_SCHOOL = MODEL_VERIFY_TYPE_SCHOOL = 1
MODEL_MAIL_TYPE_WORK = MODEL_VERIFY_TYPE_WORK = 2
VERIFY_CHOICE_LIST = [u"无认证", u"教育认证", u"工作认证"]  # 可以追加元素，但不要改已有元素的顺序。因为数据库存储的枚举值对应这个数组的下标
DEFAULT_VERIFY_INDEX = 0

# MODEL_SEX_ENUMERATE
MODEL_SEX_UNKNOWN_INDEX = 0
MODEL_SEX_MALE_INDEX = 1
MODEL_SEX_FEMALE_INDEX = 2
SEX_CHOICE_LIST = [u"未知", u"男", u"女"]  # 可以追加元素，但不要改已有元素的顺序。因为数据库存储的枚举值对应这个数组的下标
DEFAULT_SEX_INDEX = 0

BIRTH_YEAR_CHOICE_LIST = range(CURRENT_YEAR - MAX_AGE, CURRENT_YEAR - MIN_AGE + 1)
DEFAULT_YEAR_INDEX = BIRTH_YEAR_CHOICE_LIST.index(DEFAULT_BIRTH_YEAR)

# MODEL_MARTIAL_STATUS_ENUMERATE
MODEL_MARTIAL_STATUS_UNKNOWN = 0
MODEL_MARTIAL_STATUS_NO_MARRY = 1
MODEL_MARTIAL_STATUS_BREAK = 2
REQUIREMENT_MARTIAL_STATUS_CHOICE_LIST = [u"未知", u"未婚", u"离异不带孩子", u"离异最多带1个孩子", u"离异最多带2个孩子", u"离异带2+个孩子"]  # 可以追加元素，但不要改已有元素的顺序。因为数据库存储的枚举值对应这个数组的下标
USER_MARTIAL_STATUS_CHOICE_LIST = [u"未知", u"未婚", u"离异不带孩子", u"离异带1个孩子", u"离异带2个孩子", u"离异带2+个孩子"]
DEFAULT_MARTIAL_STATUS_INDEX = 0

HEIGHT_CHOICE_LIST = range(MIN_HEIGHT, MAX_HEIGHT)
DEFAULT_HEIGHT_INDEX = 30

WEIGHT_CHOICE_LIST = range(MIN_WEIGHT, MAX_WEIGHT)
DEFAULT_WEIGHT_INDEX = 20

MONTH_PAY_CHOICE_LIST = range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000)
DEFAULT_MONTH_PAY_INDEX = 6

STUDY_FROM_YEAR_CHOICE_LIST = range(MIN_STUDY_FROM_YEAR, MAX_STUDY_FROM_YEAR + 1)
DEFAULT_STUDY_FROM_YEAR_INDEX = len(STUDY_FROM_YEAR_CHOICE_LIST) - 1

MATCH_INFO_DICT = {
    OP_TYPE_VERIFY: {
        "CHOICE_LIST": VERIFY_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_VERIFY_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_SEX: {
        "CHOICE_LIST": SEX_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_SEX_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_MARTIAL_STATUS: {
        "CHOICE_LIST": REQUIREMENT_MARTIAL_STATUS_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_MARTIAL_STATUS_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_BIRTH_YEAR: {
        "CHOICE_LIST": BIRTH_YEAR_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_YEAR_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_HEIGHT: {
        "CHOICE_LIST": HEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_HEIGHT_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_WEIGHT: {
        "CHOICE_LIST": WEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_WEIGHT_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_MONTH_PAY: {
        "CHOICE_LIST": MONTH_PAY_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_MONTH_PAY_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_BIRTH_YEAR_PERIOD: {
        "CHOICE_LIST": BIRTH_YEAR_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_YEAR_INDEX,
        "COLUMN_CHANGE_FUNC": "birthYearPeriodColumnChange"
    },
    OP_TYPE_HEIGHT_PERIOD: {
        "CHOICE_LIST": HEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_HEIGHT_INDEX,
        "COLUMN_CHANGE_FUNC": "heightPeriodColumnChange"
    },
    OP_TYPE_WEIGHT_PERIOD: {
        "CHOICE_LIST": WEIGHT_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_WEIGHT_INDEX,
        "COLUMN_CHANGE_FUNC": "weightPeriodColumnChange"
    },
    OP_TYPE_EDUCATION_MULTI: {
        "CHOICE_LIST": [],
        "DEFAULT_INDEX": DEFAULT_MULTI_INDEX,
        "COLUMN_CHANGE_FUNC": "updateEducationMultiColumnChange",
    },
    OP_TYPE_WORK_MULTI: {
        "CHOICE_LIST": [],
        "DEFAULT_INDEX": DEFAULT_MULTI_INDEX,
        "COLUMN_CHANGE_FUNC": "updateWorkMultiColumnChange",
    },
    OP_TYPE_MONTH_PAY_PERIOD: {
        "CHOICE_LIST": MONTH_PAY_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_MONTH_PAY_INDEX,
        "COLUMN_CHANGE_FUNC": "monthPayPeriodColumnChange"
    },
    OP_TYPE_STUDY_FROM_YEAR: {
        "CHOICE_LIST": STUDY_FROM_YEAR_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_STUDY_FROM_YEAR_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_EDUCATION_LEVEL: {
        "CHOICE_LIST": EDUCATION_LEVEL,
        "DEFAULT_INDEX": DEFAULT_EDUCATION_INDEX,
        "COLUMN_CHANGE_FUNC": ""
    },
    OP_TYPE_STUDY_FROM_YEAR_PERIOD: {
        "CHOICE_LIST": STUDY_FROM_YEAR_CHOICE_LIST,
        "DEFAULT_INDEX": DEFAULT_STUDY_FROM_YEAR_INDEX,
        "COLUMN_CHANGE_FUNC": "studyFromYearPeriodColumnChange"
    }
}

# MEET_RESULT
MODEL_MEET_RESULT_CHOICE_LIST = [x[1] for x in sorted(MODEL_MEET_RESULT_MAP.items(), key=lambda i:i[0])]
