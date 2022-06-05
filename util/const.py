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

MIN_HEIGHT = 140
GOOD_HEIGHT = 170
MAX_HEIGHT = 200

MIN_MONTH_PAY = 4000
GOOD_MONTH_PAY = 15000
MAX_MONTH_PAY = 1000000

# logic
MOBILE_SECRET = 'matchispursued'

# response
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

# rabbitmq
EXCHANGE_NAME = 'offline_script'

# 七牛
CDN_QINIU_URL = 'http://img.ggjjzhzz.cn/'
CDN_QINIU_ADDRESS_URL = 'http://img.ggjjzhzz.cn/address/'
CDN_QINIU_BOY_HEAD_IMG = CDN_QINIU_URL + 'miniprogress/user_head/boy.jpg'
CDN_QINIU_GIRL_HEAD_IMG = CDN_QINIU_URL + 'miniprogress/user_head/girl.jpg'
CDN_QINIU_UNKNOWN_HEAD_IMG = CDN_QINIU_URL + 'miniprogress/user_head/unknown.jpg'
CDN_QINIU_ADDRESS_IMG = CDN_QINIU_URL + 'miniprogress/icon/address.png'
CDN_QINIU_TIME_IMG = CDN_QINIU_URL + 'miniprogress/icon/time.png'
CDN_QINIU_LOGO = CDN_QINIU_URL + 'miniprogress/about.png'

# model
# MODEL_STATUS_ENUMERATE
MODEL_STATUS_YES = 1
MODEL_STATUS_NO = 0
# MODEL_WORK_VERIFY_STATUS_ENUMERATE
MODEL_WORK_VERIFY_STATUS_YES = 1
MODEL_WORK_VERIFY_STATUS_NO = 0
# MODEL_SEX_ENUMERATE
MODEL_SEX_UNKNOWN_INDEX = 0
MODEL_SEX_MALE_INDEX = 1
MODEL_SEX_FEMALE_INDEX = 2
# MODEL_USER_OP_TYPE_ENUMERATE  如果更改，需要同步小程序对应枚举
MODEL_USER_OP_TYPE_SEX = 'updateSex'
MODEL_USER_SEX_CHOICE_LIST = ["未知", "男", "女"]
MODEL_USER_DEFAULT_SEX_INDEX = 0
MODEL_USER_OP_TYPE_BIRTH_YEAR = 'updateBirthYear'
MODEL_USER_DEFAULT_BIRTH_YEAR = CURRENT_YEAR - GOOD_AGE
MODEL_USER_BIRTH_YEAR_START = CURRENT_YEAR - MAX_AGE
MODEL_USER_BIRTH_YEAR_END = CURRENT_YEAR - MIN_AGE + 1
MODEL_USER_BIRTH_YEAR_CHOICE_LIST = range(MODEL_USER_BIRTH_YEAR_START, MODEL_USER_BIRTH_YEAR_END)
MODEL_USER_DEFAULT_BIRTH_YEAR_INDEX = MODEL_USER_BIRTH_YEAR_CHOICE_LIST.index(CURRENT_YEAR - GOOD_AGE)
MODEL_USER_OP_TYPE_MARTIAL_STATUS = 'updateMartialStatus'
MODEL_USER_DEFAULT_MARTIAL_STATUS_INDEX = 0
MODEL_USER_MARTIAL_STATUS_CHOICE_LIST = ["未知", "未婚", "离异"]
MODEL_USER_MARTIAL_STATUS_PERIOD_CHOICE_LIST = ["不限", "未婚", "离异"]
MODEL_USER_OP_TYPE_HEIGHT = 'updateHeight'
MODEL_USER_HEIGHT_CHOICE_LIST = range(MIN_HEIGHT, MAX_HEIGHT)  # 如果有改动这个枚举，需要刷数据
MODEL_USER_DEFAULT_HEIGHT_INDEX = 30
MODEL_USER_OP_TYPE_WEIGHT = 'updateWeight'
MODEL_USER_WEIGHT_CHOICE_LIST = range(MIN_WEIGHT, MAX_WEIGHT)  # 如果有改动这个枚举，需要刷数据
MODEL_USER_DEFAULT_WEIGHT_INDEX = 20
MODEL_USER_OP_TYPE_MONTH_PAY = 'updateMonthPay'
MODEL_USER_MONTH_PAY_CHOICE_LIST = range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000)  # 如果有改动这个枚举，需要刷数据
MODEL_USER_DEFAULT_MONTH_PAY_INDEX = 6
MODEL_USER_OP_TYPE_EDUCATION = 'updateEducation'
MODEL_USER_DEFAULT_EDUCATION_INDEX = 0
MODEL_USER_EDUCATION_CHOICE_LIST = ["未知", "高中", "专科", "本科", "硕士", "博士"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_EDUCATION_PERIOD_CHOICE_LIST = ["不限", "高中", "专科", "本科", "硕士", "博士"]  # 如果有改动这个枚举，需要刷数据
MODEL_USER_OP_TYPE_BIRTH_YEAR_PERIOD = 'updateBirthYearPeriod'
MODEL_USER_OP_TYPE_HEIGHT_PERIOD = 'updateHeightPeriod'
MODEL_USER_HEIGHT_PERIOD_CHOICE_LIST = range(MIN_HEIGHT, MAX_HEIGHT)
MODEL_USER_OP_TYPE_WEIGHT_PERIOD = 'updateWeightPeriod'
MODEL_USER_WEIGHT_PERIOD_CHOICE_LIST = range(MIN_WEIGHT, MAX_WEIGHT)
MODEL_USER_OP_TYPE_MONTH_PAY_PERIOD = 'updateMonthPayPeriod'
MODEL_USER_MONTH_PAY_PERIOD_CHOICE_LIST = range(MIN_MONTH_PAY, MAX_MONTH_PAY, 1000)
MODEL_USER_OP_TYPE_EDUCATION_PERIOD = 'updateEducationPeriod'
MODEL_USER_OP_TYPE_EXTEND_1 = 'updateExtend1'
MODEL_USER_OP_TYPE_EXTEND_2 = 'updateExtend2'
MODEL_USER_OP_TYPE_EXTEND_3 = 'updateExtend3'
MODEL_USER_OP_TYPE_EXTEND_4 = 'updateExtend4'
MODEL_USER_OP_TYPE_EXTEND_5 = 'updateExtend5'
MODEL_USER_OP_TYPE_EXTEND_6 = 'updateExtend6'
MODEL_USER_OP_TYPE_EXTEND_7 = 'updateExtend7'
MODEL_USER_OP_TYPE_EXTEND_8 = 'updateExtend8'
MODEL_USER_OP_TYPE_EXTEND_9 = 'updateExtend9'
MODEL_USER_OP_TYPE_EXTEND_10 = 'updateExtend10'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_1 = 'updatePeriodExtend1'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_2 = 'updatePeriodExtend2'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_3 = 'updatePeriodExtend3'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_4 = 'updatePeriodExtend4'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_5 = 'updatePeriodExtend5'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_6 = 'updatePeriodExtend6'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_7 = 'updatePeriodExtend7'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_8 = 'updatePeriodExtend8'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_9 = 'updatePeriodExtend9'
MODEL_USER_OP_TYPE_PERIOD_EXTEND_10 = 'updatePeriodExtend10'

# MEET_RESULT
MODEL_MEET_RESULT_MAP = {
    0: "等待点评",
    1: "人不错",
    2: "不合适",
    3: "信息造假",
    4: "迟到爽约",
    5: "太小气",
    6: "邋里邋遢"
}
MODEL_MEET_RESULT_CHOICE_LIST = [x[1] for x in sorted(MODEL_MEET_RESULT_MAP.items(), key=lambda i:i[0])]


# GUAN_INFO_OP_TYPE_ENUMERATE
GUAN_INFO_OP_TYPE_INVITE = 1  # 邀请
GUAN_INFO_OP_TYPE_JOIN = 2  # 加入
GUAN_INFO_OP_TYPE_QUIT = 3  # 退出

# MINI_PROGRAM
PICKER_TYPE_SELECTOR = 0
PICKER_TYPE_MULTI_SELECTOR = 1
ABOUT_PAGE = '/page/about/about?title=关于我们'  # 关于我们
SECRET_PAGE = '/page/secret/secret?title=隐私条款'  # 隐私条款
SHARE_PAGE = '/page/share/share'  # 分享
SUGGESTION_PAGE = '/page/suggestion/suggestion'  # 客服（建议）
GUANINFO_PAGE = '/page/guan_info/guan_info?guan_id={guan_id}'  # 活动详情页
MYINFORMATION_PAGE = '/page/my_information/my_information?title=我的资料'  # 我的资料
MYINFORMATION_PAGE_WITH_ERRMSG = '/page/my_information/my_information?title=我的资料&errMsg=请完善个人信息'  # 我的资料
MYREQUIREMENT_PAGE = '/page/my_requirement/my_requirement?title=见面条件'  # 见面条件
WORKVERIFY_PAGE = '/page/work_verify/work_verify'  # 工作认证
GUANINFO_SHORT_PAGE = 'guan_info/guan_info?guan_id={guan_id}'  # 活动详情页
SUBSCRIBE_ACTIVITY_START_NOTI_TID = '0LeRGd69AHugmAOYDLHxut1DBZhpkZUdZb5f57DeD3g'  # 活动开始前推送的模板消息
WX_MINIPROGRAM_GET_TEKEN = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'
WX_MINIPROGRAM_CODE_TO_SESSION = 'https://api.weixin.qq.com/sns/jscode2session?'
WX_MINIPROGRAM_SEND_SUBSCRIBE_MSG = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}'