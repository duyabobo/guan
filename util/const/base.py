#! /usr/bin/env python
# -*- coding: utf-8 -*-

ALL_STR = u"全部"
# logic
MOBILE_SECRET = 'matchispursued'

# response

# rabbitmq
EXCHANGE_NAME = 'offline_script'

# GUAN_INFO_OP_TYPE_ENUMERATE
GUAN_INFO_OP_TYPE_INVITE = 1  # 邀请
GUAN_INFO_OP_TYPE_JOIN = 2  # 加入
GUAN_INFO_OP_TYPE_QUIT = 3  # 退出
import datetime

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

MODEL_MEET_RESULT_MAP = {
    0: "等待点评",
    1: "人不错",
    2: "信息造假",
    3: "迟到爽约",
    4: "太小气",
    5: "衣冠不得体"
}
