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
#   0会展示1月，1月内不操作会自动转化为2。
#   1/2 会持续展示在自己首页的。
#   3/4/5/6是会继续展示1周的。
# 另外：
#   见面结论任何变更会通过icon同步给对方。0是头像icon，1是实心爱心，2是空心爱心，3/4/5/6是加油。
#   如果双方都选择了1/2，则停止推荐新的活动。
MODEL_MEET_RESULT_MAP = {
    0: "尚未表达意向",
    1: "合适（主动选择意向）",
    2: "合适（系统猜测意向）",
    3: "不合适（信息造假）",
    4: "不合适（迟到爽约）",
    5: "不合适（衣冠不得体）",
    6: "不合适（性格不合）",
}
