#! /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import requests

import util.config
from model.passport import Passport
from ral.passport import put_current_user_info
from util.encode import generate_access_token


class WxHelper(object):
    def __init__(self):
        pass

    @classmethod
    def get_openid_by_code(cls, js_code):
        """使用小程序返回的code，请求wx的接口查询openid"""
        url_params = urllib.urlencode(
            {
                'js_code': js_code,
                'appid': util.config.get("weixin", "appid"),
                'secret': util.config.get("weixin", "secret"),
                'grant_type': util.config.get("weixin", "grant_type")
            }
        )

        wx_code_to_session_url = util.config.get("weixin", "code_to_session_url")
        wx_auth_url = wx_code_to_session_url + url_params
        wx_auth_res = requests.get(wx_auth_url, timeout=3).json()
        return wx_auth_res.get("openid", None)


class LoginService(object):
    def __init__(self, db_session, redis):
        self.db_session = db_session
        self.redis = redis

    def login(self, openid):
        """检查用户记录，如果不存在就新增，并对该用户创建session"""
        passport = Passport.get_by_openid(self.db_session, openid)
        if not passport:
            passport = Passport.add_by_openid(self.db_session, openid)

        access_token = generate_access_token(passport.id)
        current_user_info_json = put_current_user_info(self.redis, access_token, passport)
        return access_token, current_user_info_json
