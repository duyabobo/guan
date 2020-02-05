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
RESP_OFFLINE_MEETING_DUPLICATE = {'code': 1011, 'errmsg': u'每天只能参加一个线下活动'}
RESP_OFFLINE_AUTH_CHECK_FAILED = {'code': 1012, 'errmsg': u'权限检查不通过'}

# normal
YES = 1
NO = 0

# ANSWER_INFO_ID
ANSWER_INFO_ID_FEMALE = 1
ANSWER_INFO_ID_MALE = 2
SEX_DICT = {
    ANSWER_INFO_ID_FEMALE: '女',
    ANSWER_INFO_ID_MALE: '男'
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

# GUANGUAN_STATUS
GUANGUAN_STATUS_ONLINE = 1
GUANGUAN_STATUS_OFFLINE = 2

# DEGREE
DEGREE_DICT = {
    0: '专科',
    1: '三本',
    2: '二本',
    3: '一本',
    4: '双一流',
    5: '国外'
}

# GUAN_TYPE_ID
GUAN_TYPE_ID_MEET = 2

# GUAN_INFO_ID
GUAN_INFO_ID_USER_INFO = 1

# AUTH_USER_ID_DICT
AUTH_USER_ID_DICT = {
    'admin': ['3']
}

# rabbitmq
EXCHANGE_NAME = 'offline_script'
