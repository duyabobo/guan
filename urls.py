#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from api import example
from api import guan_answer
from api import guan_evaluation
from api import guan_info
from api import guan_point
from api import guanguan
from api import index
from api import init
from api import login
from api import suggestion
from api import user

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/index$', index.IndexHandler),
    (r'/init$', init.InitHandler),
    (r'/login$', login.LoginHandler),
    (r'/guanguan$', guanguan.GuanGuanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/guan_evaluation$', guan_evaluation.GuanEvaluationHandler),
    (r'/guan_answer$', guan_answer.GuanAnswerHandler),
    (r'/guan_point$', guan_point.GuanPointHandler),
    (r'/user$', user.UserHandler),
    (r'/suggestion$', suggestion.SuggestionHandler),
]
