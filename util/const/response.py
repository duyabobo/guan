#! /usr/bin/env python
# -*- coding: utf-8 -*-
RESP_SUCCESS_CODE = 0
RESP_OK = {'code': 0}
RESP_TOP_MONITOR_ERROR = {'code': 1001, 'errMsg': '服务器错误'}
RESP_NEED_LOGIN = {'code': 1002, 'errMsg': '需要登录'}
RESP_NEED_FILL_INFO = {'code': 1003, 'errMsg': '请完善个人信息'}
RESP_SIGN_INVALID = {'code': 1004, 'errMsg': '签名验证失败'}
RESP_HAS_EMAIL_VERIFY_RECENTLY = {'code': 1005, 'errMsg': '您半年内已经工作认证过，请联系客服修改'}
RESP_HAS_EMAIL_VERIFY_FAILED = {'code': 1006, 'errMsg': '验证码错误，请重新输入'}
RESP_HAS_EMAIL_IS_NOT_COMPANY = {'code': 1007, 'errMsg': '贵公司尚未开放认证，请联系客服'}
RESP_JOIN_ACTIVITY_FAILED = {'code': 1008, 'errMsg': '参加见面活动失败'}
RESP_HAS_ONGOING_ACTIVITY = {'code': 1009, 'errMsg': '您有进行中的见面，不能参与别的见面'}
RESP_HAS_SEND_EMAIL = {'code': 0, 'errMsg': '您已发送过认证邮件，请稍后检查'}
RESP_SEX_CANOT_EDIT = {'code': 1010, 'errMsg': '不能修改性别，请联系客服'}
RESP_USER_SEX_FIRST_EDIT = {'code': 1011, 'errMsg': '请先完善个人信息里的性别'}
RESP_REQUIREMENT_SEX_ERROR = {'code': 1012, 'errMsg': '期望性别不能与自己相同'}
RESP_SUCCESS_WITH_NOTI_MIN_CODE = 9000
RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI = {'code': 9001, 'errMsg': 'tobefilled'}
RESP_USER_INFO_UPDATE_SUCCESS_WITH_NOTI = {'code': 9002, 'errMsg': 'tobefilled'}
RESP_REQUIREMENT_UPDATE_SUCCESS_WITH_NOTI = {'code': 9003, 'errMsg': 'tobefilled'}
