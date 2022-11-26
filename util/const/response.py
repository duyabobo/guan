#! /usr/bin/env python
# -*- coding: utf-8 -*-
RESP_SUCCESS_CODE = 0
RESP_OK = {'code': 0}
RESP_TOP_MONITOR_ERROR = {'code': 1001, 'errMsg': '服务器错误'}
RESP_NEED_LOGIN = {'code': 1002, 'errMsg': '需要登录'}
RESP_NEED_FILL_INFO = {'code': 1003, 'errMsg': '请完善个人信息'}
RESP_NEED_VERIFY = {'code': 1003, 'errMsg': '请完成认证'}
RESP_NEED_FILL_SEX = {'code': 1003, 'errMsg': '请完善性别'}
RESP_NEED_FILL_BIRTH_YEAR = {'code': 1003, 'errMsg': '请完善出生年份'}
RESP_NEED_FILL_HEIGHT = {'code': 1003, 'errMsg': '请完善身高'}
RESP_NEED_FILL_WEIGHT = {'code': 1003, 'errMsg': '请完善体重'}
RESP_NEED_FILL_HOME_REGION = {'code': 1003, 'errMsg': '请完善籍贯'}
RESP_NEED_FILL_STUDY_REGION = {'code': 1003, 'errMsg': '请完善学校城市'}
RESP_NEED_FILL_STUDY_FROM_YEAR = {'code': 1003, 'errMsg': '请完善入学年份'}
RESP_NEED_FILL_EDUCATION_LEVEL = {'code': 1003, 'errMsg': '请完善学历信息'}
RESP_NEED_FILL_EDUCATION = {'code': 1003, 'errMsg': '请完善专业信息'}
RESP_NEED_FILL_MARTIAL_STATUS = {'code': 1003, 'errMsg': '请完善婚姻状态'}
RESP_NEED_FILL_WORK_REGION = {'code': 1003, 'errMsg': '请完善工作城市'}
RESP_NEED_FILL_WORK = {'code': 1003, 'errMsg': '请完善工作信息'}
RESP_NEED_FILL_MONEY_PAY = {'code': 1003, 'errMsg': '请完善税前月工资'}
RESP_SIGN_INVALID = {'code': 1004, 'errMsg': '签名验证失败'}
RESP_HAS_EMAIL_VERIFY_RECENTLY = {'code': 1101, 'errMsg': '您半年内已经工作认证过，请联系客服修改'}
RESP_HAS_EMAIL_VERIFY_FAILED = {'code': 1102, 'errMsg': '验证码错误，请重新输入'}
RESP_HAS_EMAIL_IS_NOT_COMPANY = {'code': 1103, 'errMsg': '贵公司尚未开放认证，请联系客服'}
RESP_EMAIL_IS_NOT_VALID = {'code': 1104, 'errMsg': '邮件格式不争气，请重新输入'}
RESP_JOIN_ACTIVITY_FAILED = {'code': 1201, 'errMsg': '本次见面已被别人预约，请返回重新选择'}
RESP_HAS_ONGOING_ACTIVITY = {'code': 1202, 'errMsg': '您有进行中的见面，不能参与别的见面'}
RESP_HAS_SEND_EMAIL = {'code': 0, 'errMsg': '您已发送过认证邮件，请稍后检查'}
RESP_SEX_CANOT_EDIT = {'code': 1301, 'errMsg': '不能修改性别，请联系客服'}
RESP_USER_SEX_FIRST_EDIT = {'code': 1302, 'errMsg': '请先完善个人信息里的性别'}
RESP_REQUIREMENT_SEX_ERROR = {'code': 1303, 'errMsg': '期望性别不能与自己相同'}
RESP_MARTIAL_STATUS_CANOT_EDIT = {'code': 1304, 'errMsg': '请完善真实的婚姻现状'}
RESP_NEED_INVITE_OR_MEMBER = {'code': 1401, 'errMsg': '请充会员，或邀请一位新用户注册'}
RESP_SUCCESS_WITH_NOTI_MIN_CODE = 9000
RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI = {'code': 9001, 'errMsg': 'tobefilled'}
RESP_USER_INFO_UPDATE_SUCCESS_WITH_NOTI = {'code': 9002, 'errMsg': 'tobefilled'}
RESP_REQUIREMENT_UPDATE_SUCCESS_WITH_NOTI = {'code': 9003, 'errMsg': 'tobefilled'}
