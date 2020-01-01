#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from api import example
from api import login
from api import user_info

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/login$', login.LoginHandler),
    (r'/male_user$', user_info.UserInfoHandler),
]
