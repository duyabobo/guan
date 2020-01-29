#!/usr/bin/python
# -*- coding=utf-8 -*-

# logic
MOBILE_SECRET = 'matchispursued'

# response
RESP_OK = {'code': 0}
RESP_TOP_MONITOR_ERROR = {'code': 1001, 'errmsg': u'服务器错误'}
RESP_MISSING_PARAMETER = {'code': 1002, 'errmsg': u'参数缺失'}
RESP_NEED_LOGIN = {'code': 1003, 'errmsg': u'需要登录'}
RESP_PARAMETER_ERROR = {'code': 1004, 'errmsg': u'参数错误'}
RESP_MOBILE_CODE_ERROR = {'code': 1005, 'errmsg': u'手机验证码错误'}
RESP_MOBILE_ALREADY_USED = {'code': 1006, 'errmsg': u'手机号码已经注册'}
RESP_SEX_IS_UNKNOWN = {'code': 1007, 'errmsg': u'性别未知'}
RESP_USER_IS_UNKNOWN = {'code': 1008, 'errmsg': u'用户不可达'}
RESP_SEX_OF_USER_IS_FALSE = {'code': 1009, 'errmsg': u'用户性别不支持当前操作'}
RESP_GUAN_POINT_NOT_ENOUGH = {'code': 1010, 'errmsg': u'用户积分不足'}

# normal
YES = 1
NO = 0

# USER_SEX
FEMALE = 0
MALE = 1
SEX_DICT = {
    FEMALE: '女',
    MALE: '男'
}

# USER_STATUS
USER_STATUS_NORMAL = 0
USER_STATUS_IN_DATING = 1
USER_STATUS_IN_LOVE = 2
USER_STATUS_NORMAL_BOUNDARY = 100
USER_STATUS_LOCKED_MISS_DATING = 51
USER_STATUS_LOCKED_BE_COMPAINED = 52
USER_STATUS_GOOD_BOUNDARY = 100
USER_STATUS_DELETED = 101

# DEGREE
DEGREE_DICT = {
    0: '专科',
    1: '三本',
    2: '二本',
    3: '一本',
    4: '双一流',
    5: '国外'
}

# rabbitmq
EXCHANGE_NAME = 'offline_script'
