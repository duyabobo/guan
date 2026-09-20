#! /usr/bin/env python
# -*- coding: utf-8 -*-

# MINI_PROGRAM
PICKER_TYPE_SELECTOR = 0
PICKER_TYPE_MULTI_SELECTOR = 1
PICKER_TYPE_REGION_SELECTOR = 2
PICKER_TYPE_MULTI_EXTRA_SELECTOR = 3

MATCH_CONFIG_PAGE = '/page/match_config/match_config'           # 匹配配置（聚合我的条件+期望）
MATCH_CONFIG_PAGE_WITH_ERRMSG = '/page/match_config/match_config?errMsg='  # 带错误提示

# 兼容旧引用（后续调用方统一迁移到 MATCH_CONFIG_PAGE）
MYINFORMATION_PAGE = MATCH_CONFIG_PAGE
MYINFORMATION_PAGE_WITH_ERRMSG = MATCH_CONFIG_PAGE_WITH_ERRMSG
MYREQUIREMENT_PAGE = MATCH_CONFIG_PAGE

GUANINFO_PAGE = '/page/guan_info/guan_info?guan_id={guan_id}'   # 活动详情页
GUANINFO_SHORT_PAGE = 'guan_info/guan_info?guan_id={guan_id}'   # 活动详情页（短路径）

SUBSCRIBE_ACTIVITY_START_NOTI_TID = '0LeRGd69AHugmAOYDLHxut1DBZhpkZUdZb5f57DeD3g'
WX_MINIPROGRAM_GET_TEKEN = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential'
WX_MINIPROGRAM_SEND_MSG_TO_USER = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}'
WX_MINIPROGRAM_CODE_TO_SESSION = 'https://api.weixin.qq.com/sns/jscode2session'
WX_MINIPROGRAM_SEND_SUBSCRIBE_MSG = 'https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}'
