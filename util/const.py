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
