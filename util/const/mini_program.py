#! /usr/bin/env python
# -*- coding: utf-8 -*-

# MINI_PROGRAM
PICKER_TYPE_SELECTOR = 0
PICKER_TYPE_MULTI_SELECTOR = 1
PICKER_TYPE_REGION_SELECTOR = 2
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
