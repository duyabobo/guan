#!/usr/bin/python
# -*- coding=utf-8 -*-
# 前后端的时间传输都是通过时间戳传递, 后端处理时间都是精确到秒, 时间戳 -1 对应时间 None
from datetime import datetime, timedelta


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


def datetime2str(d, fmt="%Y-%m-%d %H:%M:%S"):
    return d.strftime(fmt)


def datetime2hommization(d):
    """
    把日期转成人性化友好的字符格式：
    1. 今天就显示`今天 %H:%M:%S`
    2. 明天就显示`明天 %H:%M:%S`
    3. 后天就显示`后天 %H:%M:%S`
    4. 其他情况
    4.1 不跨年显示`%m-%d(几天后) %H:%M:%S`
    4.3 其他情况`%Y-%m-%d %H:%M:%S`
    """
    return datetime2str(d)
    today = datetime.now().date()
    days = (d.date() - today).days
    if days < 0:
        return datetime2str(d)
    elif days == 0:
        return "今天 %s" % (d.strftime("%H:%M:%S"))
    elif days == 1:
        return "明天 %s" % (d.strftime("%H:%M:%S"))
    elif days == 2:
        return "后天 %s" % (d.strftime("%H:%M:%S"))
    elif d.year == today.year:  # 不跨年
        return "%s(%d天后) %s" % (d.strftime("%m-%d"), days, d.strftime("%H:%M:%S"))
    else:
        return datetime2str(d)
