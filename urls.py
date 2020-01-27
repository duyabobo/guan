#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from api import example
from api import guan_answer
from api import guan_evaluation
from api import guan_info
from api import guanguan
from api import login

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/login$', login.LoginHandler),
    (r'/guanguan$', guanguan.GuanGuanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/guan_evaluation$', guan_evaluation.GuanEvaluationHandler),
    (r'/guan_answer$', guan_answer.GuanAnswerHandler),
]
