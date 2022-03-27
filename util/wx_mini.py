#! /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

import requests

import util.config
import util.config
from util import const


class WxHelper(object):
    def __init__(self):
        self.appid = util.config.get("weixin", "appid")
        self.secret = util.config.get("weixin", "secret")

    def getOpenidByCode(self, jsCode):
        """使用小程序返回的code，请求wx的接口查询openid"""
        urlParams = urllib.urlencode(
            {
                'js_code': jsCode,
                'appid': self.appid,
                'secret': self.secret,
                'grant_type': 'authorization_code'
            }
        )

        wxAuthUrl = const.WX_MINIPROGRAM_CODE_TO_SESSION + urlParams
        wxAuthRes = requests.get(wxAuthUrl, timeout=3).json()
        return wxAuthRes.get("openid", None)

    def getMiniProgramToken(self):
        """获取小程序请求所需的access_token，有效期目前为 2 个小时，需定时刷新"""
        getTokenUrl = const.WX_MINIPROGRAM_GET_TEKEN.format(appid=self.appid, secret=self.secret)
        tokenRes = requests.get(getTokenUrl, timeout=3).json()
        return tokenRes.get("access_token", "")

    def sendSubscribeMsg(self, openId, templateId, page, data, miniprogramState):
        """发送用户订阅消息"""
        access_token = self.getMiniProgramToken()
        sendSmsUrl = const.WX_MINIPROGRAM_SEND_SUBSCRIBE_MSG.format(access_token=access_token)
        res = requests.post(sendSmsUrl, json={
            "touser": openId,
            "template_id": templateId,
            "page": page,
            "data": data,
            "miniprogram_state": miniprogramState,
        }, timeout=3).json()
        return res
