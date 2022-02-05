#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from handler import example
from handler import index
from handler import login
from handler import mine
from handler import myself
from handler import requirement

handlers = [
    (r'/$', example.ExampleHandler),
    (r'/index$', index.IndexHandler),
    (r'/login$', login.LoginHandler),
    (r'/mine$', mine.MineHandler),
    (r'/myself$', myself.MyselfHandler),
    (r'/requirement$', requirement.RequirementHandler),
]
