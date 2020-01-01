#!/usr/bin/python
# -*- coding=utf-8 -*-

# tab
TAB_ONE = '匹配'
TAB_TWO = '约会'
TAB_THREE = '成长'
TAB_FORE = '我的'

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

# normal
YES = 1
NO = 0

# user
FEMALE = 0
MALE = 1
LOGIN_PASSWORD = 0  # 登录方式：密码登录
LOGIN_MOBILE_CODE = 1  # 登录方式：验证码登录
MOBILE_CODE_USAGE_REGISTER = 0  # 验证码用来注册
MOBILE_CODE_USAGE_LOGIN = 1  # 验证码用来登录
MOBILE_CODE_USAGE_NOTIFY = 2  # 验证码用来通知

# pay_type
# PAY_TYPE_DICT
PAY_TYPE_ALIPAY = 1  # 支付宝
PAY_TYPE_WECHAT = 2  # 微信

# share
# SHARE_TYPE_DICT
SHARE_TYPE_FRIEND = 1  # 向微信朋友圈分享
SHARE_TYPE_WECHAT = 2  # 分享给微信好友或群
SHARE_TYPE_QQ = 3  # 分享给qq好友或群
SHARE_TYPE_QQ_ZONE = 4  # 分享到qq空间
SHARE_TYPE_SINA = 5  # 分享到sina博客
SHARE_TYPE_MOBILE = 6  # 短信分享给通讯录好友  # 这个很有用，基本都是亲戚（帮助成家立业）、闺蜜或兄弟（防止惦记自己的对象）之间传播
SHARE_TYPE_NEARBY = 7  # 展示二维码给附近的人

# register
# REGISTER_TYPE_DICT
EGISTER_TYPE_SHARE = 1  # 分享注册
EGISTER_TYPE_AD = 2  # 广告二维码注册
EGISTER_TYPE_PC = 3  # 官网二维码注册
EGISTER_TYPE_OTHER_CONTENT_FLAT = 4  # 各大app平台注册

# rabbitmq
EXCHANGE_NAME = 'offline_script'
