#! /usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen

import util.config
import util.config
from ral import wx
from util.async_request import asyncRequest
from util.const.mini_program import WX_MINIPROGRAM_CODE_TO_SESSION, WX_MINIPROGRAM_GET_TEKEN, \
    WX_MINIPROGRAM_SEND_SUBSCRIBE_MSG


class WxHelper(object):
    def __init__(self):
        self.appid = util.config.get("weixin", "appid")
        self.secret = util.config.get("weixin", "secret")

    @gen.coroutine
    def getOpenidByCode(self, jsCode):
        """使用小程序返回的code，请求wx的接口查询openid"""
        urlParams = {
            'js_code': jsCode,
            'appid': self.appid,
            'secret': self.secret,
            'grant_type': 'authorization_code'
        }

        wxAuthRes = yield asyncRequest(WX_MINIPROGRAM_CODE_TO_SESSION, urlParams, timeout=3)
        raise gen.Return(wxAuthRes.get("openid", None) if wxAuthRes else None)

    @gen.coroutine
    def getMiniProgramToken(self):
        """获取小程序请求所需的access_token，有效期目前为 2 个小时，需定时刷新"""
        localToken = wx.getToken()
        if localToken:
            raise gen.Return(localToken)
        tokenRes = yield asyncRequest(
            WX_MINIPROGRAM_GET_TEKEN,
            {
                "appid": self.appid,
                "secret": self.secret
            },
            timeout=3)
        accessToken = tokenRes.get("access_token", "")
        if accessToken:
            wx.setToken(accessToken)
        raise gen.Return(localToken)

    @gen.coroutine
    def sendSubscribeMsg(self, openid, templateId, page, data, miniprogramState):
        """发送用户订阅消息"""
        access_token = yield self.getMiniProgramToken()
        sendSmsUrl = WX_MINIPROGRAM_SEND_SUBSCRIBE_MSG.format(access_token=access_token)
        res = yield asyncRequest(
            sendSmsUrl,
            {
                "touser": openid,
                "template_id": templateId,
                "page": page,
                "data": data,
                "miniprogram_state": miniprogramState,
            },
            method='POST',
            timeout=3,
        )
        raise gen.Return(res)
