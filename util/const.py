#!/usr/bin/python
# -*- coding=utf-8 -*-

# logic
MOBILE_SECRET = 'matchispursued'

# response
RESP_OK = {'code': 0}
RESP_TOP_MONITOR_ERROR = {'code': 1001, 'errMsg': '服务器错误'}
RESP_NEED_LOGIN = {'code': 1002, 'errMsg': '需要登录'}

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
# MODEL_SEX_ENUMERATE
MODEL_SEX_UNKNOWN = 0
MODEL_SEX_MALE = 1
MODEL_SEX_FEMALE = 2
