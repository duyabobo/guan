#!/usr/bin/python
# -*- coding=utf-8 -*-
# 前后端的时间传输都是通过时间戳传递, 后端处理时间都是精确到秒, 时间戳 -1 对应时间 None
from datetime import datetime


def datetime2timestamp(d):
    d = str(d)
    if d:
        return int(datetime.strptime(d, '%Y-%m-%d %H:%M:%S').strftime('%s000'))
    else:
        return -1


def timestamp2datetime(t):
    t = int(t)
    if t != -1:
        return datetime.fromtimestamp(t/1000)
    else:
        return None


def date2timestamp(d):
    d = str(d)
    if d:
        return int(datetime.strptime(d, '%Y-%m-%d').strftime('%s000'))
    else:
        return -1


def timestamp2date(t):
    t = int(t)
    if t != -1:
        return datetime.fromtimestamp(t / 1000).date()
    else:
        return None
