#! /usr/bin/env python
# -*- coding: utf-8 -*-
RESP_SUCCESS_CODE = 0
RESP_OK = {'code': 0}
RESP_TOP_MONITOR_ERROR = {'code': 1001, 'errMsg': '服务器错误'}
RESP_NEED_LOGIN = {'code': 1002, 'errMsg': '需要登录'}
RESP_IDENTITY_INCOMPLETE = {'code': 1002, 'errMsg': '请重新登录后再试'}
RESP_VOICE_MISSING = {'code': 1003, 'errMsg': '没有收到语音'}
RESP_VOICE_TOO_LARGE = {'code': 1003, 'errMsg': '语音过长，请缩短后再试'}
RESP_NEED_FILL_INFO = {'code': 1003, 'errMsg': '请完善个人信息'}
RESP_SIGN_INVALID = {'code': 1004, 'errMsg': '签名验证失败'}
RESP_JOIN_ACTIVITY_FAILED = {'code': 1201, 'errMsg': '本次见面已被别人预约，请返回重新选择'}
RESP_HAS_ONGOING_ACTIVITY = {'code': 1202, 'errMsg': '您已经有满意的发展对象，不能参与别的见面'}
RESP_HAS_TIME_CONFLICT = {'code': 1203, 'errMsg': '您有其他见面和本次时间冲突，请返回重新选择'}
RESP_MEET_RESULT_ERR = {'code': 1204, 'errMsg': '修改见面结果失败'}
RESP_SUCCESS_WITH_NOTI_MIN_CODE = 9000
RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI = {'code': 9001, 'errMsg': '取消见面活动过多会影响您的信用'}
