#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'

import urllib

import requests
from tornado.concurrent import run_on_executor

import util.config
from api.basehandler import BaseHandler
from dal.user import add_user_info_by_openid
from dal.user import get_user_info_by_openid
from ral.user import del_current_user_info
from ral.user import put_current_user_info
from util.const import RESP_NEED_LOGIN
from util.encode import generate_access_token
from util.monitor import super_monitor


class LoginHandler(BaseHandler):
    __model__ = ''

    @run_on_executor
    @super_monitor
    def get(self, *args, **kwargs):
        """微信登录注册接口
        """
        js_code = self.get_request_parameter('code')
        wx_code_to_session_url = util.config.get("weixin", "code_to_session_url")
        appid = util.config.get("weixin", "appid")
        secret = util.config.get("weixin", "secret")
        grant_type = util.config.get("weixin", "grant_type")
        url_params = urllib.urlencode(
            {
                'js_code': js_code,
                'appid': appid,
                'secret': secret,
                'grant_type': grant_type
            }
        )
        wx_auth_url = wx_code_to_session_url + url_params
        wx_auth_res = requests.get(wx_auth_url, timeout=3).json()
        if wx_auth_res.get('code'):
            return self.response(resp_normal=RESP_NEED_LOGIN)
        openid = wx_auth_res['openid']
        current_user_info = get_user_info_by_openid(self.db_session, openid)
        if not current_user_info:
            current_user_info = add_user_info_by_openid(self.db_session, openid)
        access_token = generate_access_token(current_user_info)
        current_user_info_json = put_current_user_info(self.redis, access_token, current_user_info)
        return self.response(
            resp_json={'access_token': access_token, 'current_user_info': current_user_info_json}
        )

    @run_on_executor
    @super_monitor
    def put(self, *args, **kwargs):
        """用户退出登录
        """
        del_current_user_info(self.redis, self.access_token)
        return self.response()
