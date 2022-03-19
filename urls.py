#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from handler import example
from handler.miniprogram import guan_info, guanguan, mine, about, secret
from handler.pc import index
from handler.user import login, myself, requirement
from handler.verify import email_verify, phone_verify

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/index$', index.IndexHandler),
    (r'/about$', about.AboutHandler),
    (r'/secret$', secret.SecretHandler),
    (r'/login$', login.LoginHandler),
    (r'/mine$', mine.MineHandler),
    (r'/myself$', myself.MyselfHandler),
    (r'/requirement$', requirement.RequirementHandler),
    (r'/guanguan$', guanguan.GuanguanHandler),
    (r'/guan_info$', guan_info.GuanInfoHandler),
    (r'/phone_verify$', phone_verify.PhoneVerifyHandler),
    (r'/email_verify$', email_verify.EmailVerifyHandler),
]
