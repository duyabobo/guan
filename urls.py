#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from handler import about
from handler import example
from handler import guan_info
from handler import guanguan
from handler import index
from handler import login
from handler import mine
from handler import myself
from handler import requirement
from handler import email_verify

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/index$', index.IndexHandler),
    (r'/about$', about.AboutHandler),
    (r'/login$', login.LoginHandler),
    (r'/mine$', mine.MineHandler),
    (r'/myself$', myself.MyselfHandler),
    (r'/requirement$', requirement.RequirementHandler),
    (r'/guanguan$', guanguan.GuanguanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/email_verify$', email_verify.EmailVerifyHandler),
]
