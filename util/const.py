#!/usr/bin/python
# -*- coding=utf-8 -*-

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
MODEL_USER_OP_TYPE_DEFAULT_BIRTH_YEAR = 1995
MODEL_USER_OP_TYPE_MARTIAL_STATUS = 3
MODEL_USER_OP_TYPE_MARTIAL_STATUS_CHOICE_LIST = ["未知", "未婚", "离异"]
MODEL_USER_OP_TYPE_HEIGHT = 4
MODEL_USER_OP_TYPE_HEIGHT_CHOICE_LIST = ["<140cm", "140-150cm", "150-160cm", "160-170cm", "170-180cm", ">180cm"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_WEIGHT = 5
MODEL_USER_OP_TYPE_WEIGHT_CHOICE_LIST = ["<40kg", "40-50kg", "50-60kg", "60-70kg", "70-80kg", ">80kg"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_MONTH_PAY = 6
MODEL_USER_OP_TYPE_MONTH_PAY_CHOICE_LIST = ["<4000元", "4000-10000元", "10000-20000元", "20000-30000元", "30000-50000元", ">50000元"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_EDUCATION = 7
MODEL_USER_OP_TYPE_EDUCATION_CHOICE_LIST = ["未知", "高中及以下", "专科", "本科", "硕士", "博士及以上"]  # 如果有改动这个枚举，需要刷数据

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
