#! /usr/bin/env python
# -*- coding: utf-8 -*-
from util.const.meet_fee import fee_confirm_hint, no_show_toast

RESP_SUCCESS_CODE = 0
RESP_OK = {'code': 0}
RESP_TOP_MONITOR_ERROR = {'code': 1001, 'errMsg': '服务器错误'}
RESP_NEED_LOGIN = {'code': 1002, 'errMsg': '需要登录'}
RESP_IDENTITY_INCOMPLETE = {'code': 1002, 'errMsg': '请重新登录后再试'}
RESP_VOICE_MISSING = {'code': 1003, 'errMsg': '没有收到语音'}
RESP_VOICE_TOO_LARGE = {'code': 1003, 'errMsg': '语音过长，请缩短后再试'}
RESP_NEED_FILL_INFO = {'code': 1003, 'errMsg': '请完善个人信息'}
RESP_VOICE_IN_PROGRESS = {'code': 1003, 'errMsg': '已经约好见面或确认合适，暂时不能再录音'}
RESP_EXPECT_SAME_SEX = {'code': 1003, 'errMsg': '目前只支持异性期望，请改成异性后再试'}
RESP_SIGN_INVALID = {'code': 1004, 'errMsg': '签名验证失败'}
RESP_PHONE_INVALID = {'code': 1005, 'errMsg': '请填写手机号'}
RESP_PHONE_CODE_TOO_SOON = {'code': 1005, 'errMsg': '请稍后再获取验证码'}
RESP_SMS_UNAVAILABLE = {'code': 1005, 'errMsg': '验证码暂时发不出去'}
RESP_PHONE_BIND_FAILED = {'code': 1005, 'errMsg': '验证码不正确'}
RESP_PROFILE_CONFLICT_CODE = 9002
RESP_JOIN_ACTIVITY_FAILED = {'code': 1201, 'errMsg': '本次见面已被别人预约，请返回重新选择'}
RESP_HAS_APPOINTMENT = {'code': 1202, 'errMsg': '已经有一场约好的见面，不能再约别的'}
RESP_HAS_FIT_PARTNER = {'code': 1205, 'errMsg': '已经有合适的对象，不能再约或再选合适'}
RESP_HAS_TIME_CONFLICT = {'code': 1203, 'errMsg': '您有其他见面和本次时间冲突，请返回重新选择'}
RESP_MEET_RESULT_ERR = {'code': 1204, 'errMsg': '修改见面结果失败'}
RESP_MEET_FEE_CODE = 1206
RESP_MEET_FEE_OPENID = {'code': 1207, 'errMsg': '需要微信身份才能支付，请重新进入小程序'}
RESP_MEET_FEE_UNAVAILABLE = {'code': 1208, 'errMsg': '见面付费还没开通，请稍后再试'}
RESP_MEET_FEE_PENDING = {'code': 1206, 'errMsg': '支付结果确认中，请再试一次'}
RESP_SUCCESS_WITH_NOTI_MIN_CODE = 9000
RESP_GUAN_INFO_UPDATE_SUCCESS_WITH_NOTI = {'code': 9001, 'errMsg': '取消见面活动过多会影响您的信用'}
RESP_NO_SHOW_CODE = 9003


def meet_fee_required_msg(no_show_count):
    return {'code': RESP_MEET_FEE_CODE, 'errMsg': fee_confirm_hint(no_show_count)}


def no_show_recorded_msg(no_show_count):
    """已约上后取消。code 大于 9000，座位变更仍会提交。"""
    return {'code': RESP_NO_SHOW_CODE, 'errMsg': no_show_toast(no_show_count)}


def profile_conflict_msg(labels):
    """锁定资料冲突。code 大于 9000，其它字段的写入仍会提交。"""
    names = "、".join(labels)
    return {
        'code': RESP_PROFILE_CONFLICT_CODE,
        'errMsg': '%s和已保存的不一致，已保留原来的，请等待人工客服确认' % names,
    }
