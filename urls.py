#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from api import example
from api import guan_evaluation
from api import guan_info
from api import guanguan
from api import login
from api import user_info

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/login$', login.LoginHandler),
    (r'/user_info$', user_info.UserInfoHandler),
    (r'/guanguan$', guanguan.GuanGuanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/guan_evaluation$', guan_evaluation.GuanEvaluationHandler),
]
