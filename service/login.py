#! /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

import requests

import util.config
from model.passport import PassportModel
from model.user import UserModel
from ral.passport import putSession
from service import BaseService
from util.encode import generate_access_token


class WxHelper(object):
    def __init__(self):
        pass

    @classmethod
    def getOpenidByCode(cls, jsCode):
        """使用小程序返回的code，请求wx的接口查询openid"""
        urlParams = urllib.urlencode(
            {
                'js_code': jsCode,
                'appid': util.config.get("weixin", "appid"),
                'secret': util.config.get("weixin", "secret"),
                'grant_type': util.config.get("weixin", "grant_type")
            }
        )

        wxCodeToSessionUrl = util.config.get("weixin", "code_to_session_url")
        wxAuthUrl = wxCodeToSessionUrl + urlParams
        wxAuthRes = requests.get(wxAuthUrl, timeout=3).json()
        return wxAuthRes.get("openid", None)


class LoginService(BaseService):

    def login(self, openid):
        """检查用户记录，如果不存在就新增，并对该用户创建session"""
        passport = PassportModel.getByOpenid(self.dbSession, openid)
        if not passport:
            passport = PassportModel.addByOpenid(self.dbSession, openid)
            UserModel.addByPassportId(self.dbSession, passport.id)

        accessToken = generate_access_token(passport.id)
        currentUserInfoJson = putSession(self.redis, accessToken, passport)
        return accessToken, currentUserInfoJson
