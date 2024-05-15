#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

ALL_STR = u"全部"
EMPTY_STR = u""
UNKNOWN_STR = u"未知"
NO_LIMIT_STR = u"不限"
# logic
MOBILE_SECRET = 'matchispursued'

# response

# rabbitmq
EXCHANGE_NAME = 'offline_script'

# GUAN_INFO_OP_TYPE_ENUMERATE
GUAN_INFO_OP_TYPE_INVITE = 1  # 邀请
GUAN_INFO_OP_TYPE_JOIN = 2  # 加入
GUAN_INFO_OP_TYPE_QUIT = 3  # 退出

# BASE
CURRENT_YEAR = datetime.datetime.now().year
MIN_AGE = 18
GOOD_AGE = 22
MAX_AGE = 100
DEFAULT_BIRTH_YEAR = CURRENT_YEAR - GOOD_AGE

MIN_WEIGHT = 40
GOOD_WEIGHT = 60
MAX_WEIGHT = 200

MIN_HEIGHT = 140
GOOD_HEIGHT = 170
MAX_HEIGHT = 200

MIN_MONTH_PAY = 4000
GOOD_MONTH_PAY = 15000
MAX_MONTH_PAY = 1000000

MIN_STUDY_FROM_YEAR = CURRENT_YEAR - 6  # 博士6年
MAX_STUDY_FROM_YEAR = CURRENT_YEAR

# 根据自己的选择结果，影响活动结束后在首页的展示。
#   见面时间开始以后，0/1 会持续展示在自己首页，且不会推荐其他见面。
#   >= 100 是会继续展示7天(如下)，但是不影响其他见面。
UNFIX_SHOW_DELAY_DAYS = 7
# 另外：
#   见面结论任何变更会通过icon同步给对方。0是虚拟头像icon，1是真实头像icon。
MODEL_MEET_RESULT_UNKNOWN = 0
MODEL_MEET_RESULT_FIT_CHOICE = 1
MODEL_MEET_RESULT_UNFIT_CHOICE = 100
MODEL_MEET_RESULT_MAP = {
    MODEL_MEET_RESULT_UNKNOWN: "尚未表达意向",
    MODEL_MEET_RESULT_FIT_CHOICE: "合适",
    MODEL_MEET_RESULT_UNFIT_CHOICE: "不合适",
    101: "不合适（信息造假）",  # > 100的选择，会扣除保证金，而且会展示在自己的信息中（直到联系客服解除）
    102: "不合适（迟到爽约）",
    103: "不合适（涉嫌pua）",
    104: "不合适（骗财骗色）",
    105: "不合适（其他违法行为）",
}
