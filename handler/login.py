#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from handler.basehandler import BaseHandler
from ral.passport import del_current_user_info
from service.login import WxHelper, LoginService
from util.const import RESP_NEED_LOGIN
from util.monitor import super_monitor


class LoginHandler(BaseHandler):
    __model__ = ''

    @super_monitor
    def get(self, *args, **kwargs):
        """微信登录注册接口
        """
        js_code = self.get_request_parameter('code')
        openid = WxHelper.get_openid_by_code(js_code)
        if not openid:
            return self.response(resp_normal=RESP_NEED_LOGIN)

        access_token, current_user_info = LoginService(self.db_session, self.redis).login(openid)
        return self.response(
            resp_json={'access_token': access_token, 'current_user_info': current_user_info}
        )

    @super_monitor
    def put(self, *args, **kwargs):
        """用户退出登录
        """
        del_current_user_info(self.redis, self.access_token)
        return self.response()
