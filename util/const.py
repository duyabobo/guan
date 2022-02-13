#!/usr/bin/python
# -*- coding=utf-8 -*-
import datetime

# BASE
CURRENT_YEAR = datetime.datetime.now().year
MIN_AGE = 18
GOOD_AGE = 22
MAX_AGE = 100

MIN_WEIGHT = 40
GOOD_WEIGHT = 60
MAX_WEIGHT = 200

# logic
MOBILE_SECRET = 'matchispursued'

# response
RESP_OK = {'code': 0}
RESP_TOP_MONITOR_ERROR = {'code': 1001, 'errMsg': '服务器错误'}
RESP_NEED_LOGIN = {'code': 1002, 'errMsg': '需要登录'}
RESP_NEED_FILL_INFO = {'code': 1003, 'errMsg': '请完善个人信息'}

# rabbitmq
EXCHANGE_NAME = 'offline_script'

# 七牛
CDN_QINIU_URL = 'http://img.ggjjzhzz.cn/'
CDN_QINIU_BOY_HEAD_IMG = CDN_QINIU_URL + 'boy.jpg'
CDN_QINIU_GIRL_HEAD_IMG = CDN_QINIU_URL + 'girl.jpg'
CDN_QINIU_UNKNOWN_HEAD_IMG = CDN_QINIU_URL + 'unknown.jpg'
CDN_QINIU_ADDRESS_IMG = CDN_QINIU_URL + 'address.png'
CDN_QINIU_TIME_IMG = CDN_QINIU_URL + 'time.png'

# model
# MODEL_STATUS_ENUMERATE
MODEL_STATUS_YES = 1
MODEL_STATUS_NO = 0
# MODEL_WORK_VERIFY_STATUS_ENUMERATE
MODEL_WORK_VERIFY_STATUS_YES = 1
MODEL_WORK_VERIFY_STATUS_NO = 0
# MODEL_SEX_ENUMERATE
MODEL_SEX_UNKNOWN = 0
MODEL_SEX_MALE = 1
MODEL_SEX_FEMALE = 2
# MODEL_USER_OP_TYPE_ENUMERATE  如果更改，需要考虑小程序对应关系
MODEL_USER_OP_TYPE_VERIFY = 0
MODEL_USER_OP_TYPE_SEX = 1
MODEL_USER_OP_TYPE_SEX_CHOICE_LIST = ["未知", "男", "女"]
MODEL_USER_OP_TYPE_BIRTH_YEAR = 2
MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR = CURRENT_YEAR - GOOD_AGE
MODEL_USER_OP_TYPE_BIRTH_YEAR_START = CURRENT_YEAR - MAX_AGE
MODEL_USER_OP_TYPE_BIRTH_YEAR_END = CURRENT_YEAR - MIN_AGE + 1
MODEL_USER_OP_TYPE_MARTIAL_STATUS = 3
MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST = ["未知", "未婚", "离异"]
MODEL_USER_OP_TYPE_HEIGHT = 4
MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST = ["<145", "145-150", "150-155", "155-160", "160-165", "165-170", "170-175", "175-180", "180-185", ">185"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_DEFAULT_HEIGHT_INDEX = 5
MODEL_USER_OP_TYPE_WEIGHT = 5
MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST = ["<40", "40-45", "45-50", "50-55", "55-60", "60-65", "65-70", "70-75", "75-80", ">80"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_DEFAULT_WEIGHT_INDEX = 3
MODEL_USER_OP_TYPE_MONTH_PAY = 6
MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST = ["<4000", "4000-6000", "6000-10000", "10000-15000", "15000-20000", "20000-30000", "30000-40000", "40000-60000", "60000-80000", ">80000"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_DEFAULT_MONTH_PAY_INDEX = 3
MODEL_USER_OP_TYPE_EDUCATION = 7
MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST = ["未知", "高中及以下", "专科", "本科", "硕士", "博士及以上"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD = 8
MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD_ARRAY = range(MODEL_USER_OP_TYPE_BIRTH_YEAR_START, MODEL_USER_OP_TYPE_BIRTH_YEAR_END)
MODEL_USER_OP_TYPE_HEIGHT_PERIOD = 9
MODEL_USER_OP_TYPE_WEIGHT_PERIOD = 10
MODEL_USER_OP_TYPE_WEIGHT_PERIOD_ARRAY = range(MIN_WEIGHT, MAX_WEIGHT)
MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD = 11

# GUAN_INFO_OP_TYPE_ENUMERATE
GUAN_INFO_OP_TYPE_INVITE = 0  # 成为邀请人
GUAN_INFO_OP_TYPE_ACCEPT = 1  # 成为接受人
GUAN_INFO_OP_TYPE_INVITE_QUIT = 2  # 邀请人退出
GUAN_INFO_OP_TYPE_ACCEPT_QUIT = 3  # 接受人退出
GUAN_INFO_OP_TYPE_ACCEPT_UNKNOWN = 99  # 未知操作类型

# MINI_PROGRAM
ABOUT_PAGE = '/page/about/about'  # 关于
SETTING_PAGE = '/page/setting/setting'  # 设置
SHARE_PAGE = '/page/share/share'  # 分享
SUGGESTION_PAGE = '/page/suggestion/suggestion'  # 客服（建议）
MYINFORMATION_PAGE = '/page/my_information/my_information?errMsg='  # 我的资料
MYREQUIREMENT_PAGE = '/page/my_requirement/my_requirement'  # 我的期望
WORKVERIFY_PAGE = '/page/work_verify/work_verify'  # 工作认证
